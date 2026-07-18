from __future__ import annotations

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from significant_places_model import (
    CSV_HEADER,
    Config,
    KnownPlace,
    Record,
    Sample,
    SignificantPlacesSimulator,
    load_config,
    load_records,
    load_samples,
)
from build_b004_transactional_backup import build as build_b004
from build_b005_csv_recovery_backup import (
    SCRIPT_MARKER as B005_SCRIPT_MARKER,
    build as build_b005,
)
from build_injected_location_test_backup import build as build_injected_location_test
from validate_tasker_xml import validate


def sample(minutes: int, lat: float, lon: float, accuracy: float = 10) -> Sample:
    return Sample(datetime(2026, 1, 15, 8, 0) + timedelta(minutes=minutes), lat, lon, accuracy)


class SimulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config()

    def test_basic_route_confirms_second_place_with_arrival_timestamp(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        results = [simulator.process(item) for item in load_samples(ROOT / "tests/fixtures/basic_route.csv")]
        self.assertEqual([result.event for result in results][-1], "place_confirmed")
        self.assertEqual(len(simulator.records), 2)
        self.assertEqual(simulator.records[1].place_id, 2)
        self.assertEqual(simulator.records[1].timestamp, datetime(2026, 1, 15, 8, 4))

    def test_invalid_accuracy_does_not_change_state(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        simulator.process(sample(0, 0, 0))
        result = simulator.process(sample(2, 0, 0.002, 100))
        self.assertEqual(result.event, "invalid_fix")
        self.assertEqual(len(simulator.records), 1)
        self.assertIsNone(simulator.state.candidate_since)

    def test_invalid_coordinate_range_is_rejected(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        self.assertEqual(simulator.process(sample(0, 91, 0)).event, "invalid_fix")
        self.assertEqual(simulator.process(sample(0, 0, 181)).event, "invalid_fix")
        self.assertEqual(simulator.records, [])

    def test_negative_accuracy_is_rejected(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        self.assertEqual(simulator.process(sample(0, 0, 0, -1)).event, "invalid_fix")
        self.assertEqual(simulator.records, [])

    def test_coordinate_and_accuracy_boundaries_are_accepted(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        result = simulator.process(sample(0, 90, 180, self.config.gps_max_accuracy_meters))
        self.assertEqual(result.event, "day_initialized")

    def test_short_stop_is_discarded_on_return(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        simulator.process(sample(0, 0, 0))
        simulator.process(sample(2, 0, 0.002))
        simulator.process(sample(4, 0, 0.00201))
        result = simulator.process(sample(6, 0, 0.00001))
        self.assertEqual(result.event, "same_place")
        self.assertEqual(len(simulator.records), 1)

    def test_known_place_uses_nearest_matching_name(self) -> None:
        known = [
            KnownPlace("wide", "Wide", 0, 0, 100),
            KnownPlace("near", "Near", 0, 0.0001, 100),
        ]
        simulator = SignificantPlacesSimulator(self.config, known)
        result = simulator.process(sample(0, 0, 0.00009))
        self.assertEqual(result.record.name, "Near")

    def test_day_change_resets_place_id(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        simulator.process(sample(0, 0, 0))
        next_day = Sample(datetime(2026, 1, 16, 0, 1), 0, 0.002, 10)
        result = simulator.process(next_day)
        self.assertEqual(result.event, "day_initialized")
        self.assertEqual(result.record.place_id, 1)

    def test_recovery_uses_last_record_and_max_id(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        records = [
            Record(datetime(2026, 1, 15, 8, 0), 0, 0, 1, "Luogo_1"),
            Record(datetime(2026, 1, 15, 9, 0), 0, 0.002, 4, "Luogo_4"),
        ]
        self.assertTrue(simulator.recover_from_records(records, "2026-01-15"))
        self.assertEqual(simulator.state.place_counter, 4)
        self.assertEqual(simulator.state.current_lon, 0.002)

    def test_recovery_accepts_duplicate_ids_and_uses_next_safe_counter(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        records = [
            Record(datetime(2026, 1, 15, 8, 0), 0, 0, 4, "Luogo_4"),
            Record(datetime(2026, 1, 15, 9, 0), 0, 0.002, 4, "Luogo_4_dup"),
            Record(datetime(2026, 1, 15, 10, 0), 0, 0.004, 2, "Luogo_2_late"),
        ]
        self.assertTrue(simulator.recover_from_records(records, "2026-01-15"))
        self.assertEqual(simulator.state.current_id, 2)
        self.assertEqual(simulator.state.place_counter, 4)
        simulator.process(sample(122, 0, 0.006))
        result = simulator.process(sample(128, 0, 0.006))
        self.assertEqual(result.event, "place_confirmed")
        self.assertEqual(result.record.place_id, 5)

    def test_recovery_rejects_records_from_another_day_without_mutating_state(self) -> None:
        simulator = SignificantPlacesSimulator(self.config)
        records = [Record(datetime(2026, 1, 14, 23, 59), 0, 0, 1, "Luogo_1")]
        with self.assertRaises(ValueError):
            simulator.recover_from_records(records, "2026-01-15")
        self.assertIsNone(simulator.state.log_date)
        self.assertEqual(simulator.records, [])

    def test_header_only_csv_is_valid_but_has_no_recovery_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "header-only.csv"
            path.write_text(CSV_HEADER + "\n", encoding="utf-8")
            records = load_records(path)
            simulator = SignificantPlacesSimulator(self.config)
            self.assertEqual(records, [])
            self.assertFalse(simulator.recover_from_records(records, "2026-01-15"))

    def test_empty_or_malformed_recovery_csv_fails_closed(self) -> None:
        bad_contents = (
            "",
            "WRONG;HEADER\n",
            CSV_HEADER + "\n2026-01-15 08.00;91;0;1;Bad\n",
            CSV_HEADER + "\n2026-01-15 08.00;0;0;0;Bad\n",
            CSV_HEADER + "\n2026-01-15 08.00;0;0;1;\n",
            CSV_HEADER + "\n2026-01-15 09.00;0;0;1;A\n2026-01-15 08.00;0;0;2;B\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            for index, content in enumerate(bad_contents):
                path = Path(directory) / f"bad-{index}.csv"
                path.write_text(content, encoding="utf-8")
                with self.subTest(index=index), self.assertRaises(ValueError):
                    load_records(path)

    def test_config_rejects_stop_time_below_one_minute(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.csv"
            path.write_text("MIN_STOP_MINUTES=0.5\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)


class ValidatorTests(unittest.TestCase):
    def test_repository_export_has_no_blocking_errors(self) -> None:
        findings = validate(ROOT / "significant_places_tasker.xml", ROOT / "config/tasker_globals.csv")
        self.assertFalse([finding for finding in findings if finding.level == "ERROR"])
        warning_codes = {finding.code for finding in findings if finding.level == "WARN"}
        self.assertNotIn("FALLBACK_MISMATCH", warning_codes)
        self.assertNotIn("INIT_ACCURACY_UNCHECKED", warning_codes)
        self.assertNotIn("GPS_RANGE_UNCHECKED", warning_codes)
        self.assertNotIn("CONFIRM_COUNT_UNUSED", warning_codes)
        self.assertNotIn("STATE_BEFORE_WRITE", warning_codes)
        self.assertNotIn("CSV_RECOVERY_MISSING", warning_codes)
        self.assertNotIn("RECOVERY_DIAGNOSTICS_MISSING", warning_codes)

    def test_missing_longitude_condition_is_blocking(self) -> None:
        tree = ET.parse(ROOT / "significant_places_tasker.xml")
        init = next(task for task in tree.getroot().findall("Task") if task.findtext("nme") == "INIT_SIGNIFICANT_PLACES")
        condition_list = next(
            condition_list
            for condition_list in init.findall("./Action/ConditionList")
            if any(
                condition.findtext("lhs") == "%gl_longitude"
                for condition in condition_list.findall("Condition")
            )
        )
        longitude = next(
            condition for condition in condition_list.findall("Condition") if condition.findtext("lhs") == "%gl_longitude"
        )
        condition_list.remove(longitude)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.xml"
            tree.write(path, encoding="utf-8", xml_declaration=True)
            findings = validate(path, ROOT / "config/tasker_globals.csv")
        self.assertIn("INIT_COORDINATE_CHECK", {finding.code for finding in findings if finding.level == "ERROR"})

    def test_missing_candidate_count_condition_is_reported(self) -> None:
        tree = ET.parse(ROOT / "significant_places_tasker.xml")
        main = next(
            task
            for task in tree.getroot().findall("Task")
            if task.findtext("nme") == "LOG_SIGNIFICANT_PLACE_SAMPLE"
        )
        condition_list = next(
            condition_list
            for condition_list in main.findall("./Action/ConditionList")
            if any(
                condition.findtext("lhs") == "%CANDIDATE_CONFIRM_COUNT"
                for condition in condition_list.findall("Condition")
            )
        )
        counter = next(
            condition
            for condition in condition_list.findall("Condition")
            if condition.findtext("lhs") == "%CANDIDATE_CONFIRM_COUNT"
        )
        condition_list.remove(counter)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-counter-condition.xml"
            tree.write(path, encoding="utf-8", xml_declaration=True)
            findings = validate(path, ROOT / "config/tasker_globals.csv")
        self.assertIn("CONFIRM_COUNT_UNUSED", {finding.code for finding in findings if finding.level == "WARN"})

    def test_b004_stages_state_until_after_record_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "b004.xml"
            build_b004(ROOT / "significant_places_tasker.xml", path)
            tree = ET.parse(path)
            main = next(
                task
                for task in tree.getroot().findall("Task")
                if task.findtext("nme") == "LOG_SIGNIFICANT_PLACE_SAMPLE"
            )
            actions = sorted(
                main.findall("Action"),
                key=lambda action: int(action.attrib["sr"].removeprefix("act")),
            )
            write_index = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "410"
                and "%CANDIDATE_SINCE_TIMESTAMP;" in action.findtext("Str[@sr='arg1']", "")
            )
            current_lat_index = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "547"
                and action.findtext("Str[@sr='arg0']") == "%CURRENT_PLACE_LAT"
            )
            staged_lat_index = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "547"
                and action.findtext("Str[@sr='arg0']") == "%next_place_lat"
            )
            self.assertLess(staged_lat_index, write_index)
            self.assertGreater(current_lat_index, write_index)
            findings = validate(path, ROOT / "config/tasker_globals.csv")
            self.assertNotIn("STATE_BEFORE_WRITE", {item.code for item in findings})

    def test_injected_location_backup_is_isolated_and_keeps_b004_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.xml"
            path = Path(directory) / "injected.xml"
            source_tree = ET.parse(ROOT / "significant_places_tasker.xml")
            for index, (name, value) in enumerate(
                (
                    ("%LOG_DIR", "/storage/emulated/0/_SignificantPlaces"),
                    ("%MIN_STOP_MINUTES", "5"),
                )
            ):
                variable = ET.SubElement(source_tree.getroot(), "Variable", {"sr": f"testvar{index}"})
                ET.SubElement(variable, "n").text = name
                ET.SubElement(variable, "v").text = value
            source_tree.write(source, encoding="utf-8", xml_declaration=True)
            build_injected_location_test(source, path)
            tree = ET.parse(path)
            root = tree.getroot()
            variables = {item.findtext("n"): item.findtext("v") for item in root.findall("Variable")}
            self.assertEqual(
                variables["%LOG_DIR"],
                "/storage/emulated/0/_SignificantPlaces/TestData/injected-B004",
            )
            self.assertEqual(variables["%MIN_STOP_MINUTES"], "1")

            main = next(
                task
                for task in root.findall("Task")
                if task.findtext("nme") == "LOG_SIGNIFICANT_PLACE_SAMPLE"
            )
            actions = sorted(
                main.findall("Action"),
                key=lambda action: int(action.attrib["sr"].removeprefix("act")),
            )
            self.assertEqual(len(actions), 87)
            self.assertFalse([action for action in actions if action.findtext("code") == "366"])
            injected = [
                (action.findtext("Str[@sr='arg0']"), action.findtext("Str[@sr='arg1']"))
                for action in actions[18:21]
            ]
            self.assertEqual(
                injected,
                [
                    ("%gl_latitude", "0.000000"),
                    ("%gl_longitude", "0.000000"),
                    ("%gl_coordinates_accuracy", "3"),
                ],
            )

            write_index = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "410"
                and "%CANDIDATE_SINCE_TIMESTAMP;" in action.findtext("Str[@sr='arg1']", "")
            )
            for name in (
                "%PLACE_COUNTER",
                "%CURRENT_PLACE_ID",
                "%CURRENT_PLACE_NAME",
                "%CURRENT_PLACE_LAT",
                "%CURRENT_PLACE_LON",
            ):
                commit_index = next(
                    index
                    for index, action in enumerate(actions)
                    if action.findtext("code") == "547"
                    and action.findtext("Str[@sr='arg0']") == name
                )
                self.assertGreater(commit_index, write_index)

            findings = validate(path, ROOT / "config/tasker_globals.csv")
            self.assertFalse([finding for finding in findings if finding.level == "ERROR"])

    def test_b005_recovers_existing_csv_and_fails_closed_when_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "b005.xml"
            build_b005(ROOT / "significant_places_tasker.xml", path)
            tree = ET.parse(path)
            root = tree.getroot()
            init = next(
                task
                for task in root.findall("Task")
                if task.findtext("nme") == "INIT_SIGNIFICANT_PLACES"
            )
            main = next(
                task
                for task in root.findall("Task")
                if task.findtext("nme") == "LOG_SIGNIFICANT_PLACE_SAMPLE"
            )
            actions = sorted(
                init.findall("Action"),
                key=lambda action: int(action.attrib["sr"].removeprefix("act")),
            )
            self.assertEqual(len(actions), 82)
            self.assertEqual(len(main.findall("Action")), 85)
            self.assertFalse([action for action in actions if action.findtext("code") == "43"])
            recovery_file_conditions = {
                (
                    action.findtext("ConditionList/Condition/op"),
                    action.findtext("ConditionList/Condition/rhs"),
                )
                for action in actions
                if action.findtext("code") == "37"
                and action.findtext("ConditionList/Condition/lhs") == "%rec_type"
            }
            self.assertEqual(recovery_file_conditions, {("12", "")})

            parser_actions = [
                action
                for action in actions
                if B005_SCRIPT_MARKER in action.findtext("Str[@sr='arg0']", "")
            ]
            self.assertEqual(len(parser_actions), 1)
            parser_text = parser_actions[0].findtext("Str[@sr='arg0']", "")
            self.assertIn("&&", parser_text)
            self.assertNotIn("&amp;", parser_text)
            self.assertIn("errorCode || 'none'", parser_text)

            recovered_if = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "37"
                and action.findtext("ConditionList/Condition/lhs") == "%recovery_status"
                and action.findtext("ConditionList/Condition/rhs") == "recovered"
            )
            recovered_stop = next(
                index
                for index in range(recovered_if + 1, len(actions))
                if actions[index].findtext("code") == "137"
            )
            for name in (
                "%PLACE_COUNTER",
                "%CURRENT_PLACE_LAT",
                "%CURRENT_PLACE_LON",
                "%CURRENT_PLACE_ID",
                "%CURRENT_PLACE_NAME",
            ):
                commit_index = next(
                    index
                    for index in range(recovered_if + 1, recovered_stop)
                    if actions[index].findtext("code") == "547"
                    and actions[index].findtext("Str[@sr='arg0']") == name
                )
                self.assertLess(commit_index, recovered_stop)

            malformed_if = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "37"
                and action.findtext("ConditionList/Condition/lhs") == "%recovery_status"
                and action.findtext("ConditionList/Condition/rhs") == "malformed"
            )
            malformed_stop = next(
                action
                for action in actions[malformed_if + 1 :]
                if action.findtext("code") == "137"
            )
            self.assertEqual(malformed_stop.find("Int[@sr='arg0']").get("val"), "1")

            header_write = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "410"
                and action.findtext("Str[@sr='arg1']") == CSV_HEADER
            )
            initial_records = [
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "410"
                and action.findtext("Str[@sr='arg1']")
                == "%timestamp;%CURRENT_PLACE_LAT;%CURRENT_PLACE_LON;%CURRENT_PLACE_ID;%CURRENT_PLACE_NAME"
            ]
            self.assertEqual(len(initial_records), 2)

            new_if = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "37"
                and action.findtext("ConditionList/Condition/lhs") == "%recovery_status"
                and action.findtext("ConditionList/Condition/rhs") == "new"
            )
            contradictory_exists = next(
                index
                for index in range(new_if + 1, header_write)
                if actions[index].findtext("code") == "37"
                and actions[index].findtext("ConditionList/Condition/lhs") == "%file_exists"
                and actions[index].findtext("ConditionList/Condition/op") == "12"
            )
            contradiction_stop = next(
                action
                for action in actions[contradictory_exists + 1 : header_write]
                if action.findtext("code") == "137"
            )
            self.assertEqual(contradiction_stop.find("Int[@sr='arg0']").get("val"), "1")
            self.assertIn(initial_records[0], range(header_write + 1, len(actions)))

            header_only_if = next(
                index
                for index, action in enumerate(actions)
                if action.findtext("code") == "37"
                and action.findtext("ConditionList/Condition/lhs") == "%recovery_status"
                and action.findtext("ConditionList/Condition/rhs") == "header_only"
            )
            self.assertGreater(initial_records[1], header_only_if)
            self.assertNotIn(header_write, range(header_only_if, len(actions)))

            findings = validate(path, ROOT / "config/tasker_globals.csv")
            self.assertFalse([finding for finding in findings if finding.level == "ERROR"])


if __name__ == "__main__":
    unittest.main()
