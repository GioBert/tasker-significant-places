from __future__ import annotations

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from significant_places_model import Config, KnownPlace, Record, Sample, SignificantPlacesSimulator, load_config, load_samples
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
        self.assertEqual(simulator.records, [])

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
        self.assertIn("FALLBACK_MISMATCH", warning_codes)
        self.assertIn("STATE_BEFORE_WRITE", warning_codes)

    def test_missing_longitude_condition_is_blocking(self) -> None:
        tree = ET.parse(ROOT / "significant_places_tasker.xml")
        init = next(task for task in tree.getroot().findall("Task") if task.findtext("nme") == "INIT_SIGNIFICANT_PLACES")
        condition_list = init.find("./Action/ConditionList")
        longitude = next(
            condition for condition in condition_list.findall("Condition") if condition.findtext("lhs") == "%gl_longitude"
        )
        condition_list.remove(longitude)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.xml"
            tree.write(path, encoding="utf-8", xml_declaration=True)
            findings = validate(path, ROOT / "config/tasker_globals.csv")
        self.assertIn("INIT_COORDINATE_CHECK", {finding.code for finding in findings if finding.level == "ERROR"})


if __name__ == "__main__":
    unittest.main()
