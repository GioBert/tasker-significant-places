#!/usr/bin/env python3
"""Static, read-only checks for the Tasker project export."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


EXPECTED_TASK_ACTIONS = {
    "LOAD_CONFIG_DEFAULTS": 14,
    "INIT_SIGNIFICANT_PLACES": 32,
    "LOG_SIGNIFICANT_PLACE_SAMPLE": 80,
}


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str


def validate(xml_path: Path, config_path: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    try:
        root = ET.parse(xml_path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [Finding("ERROR", "XML_INVALID", str(exc))]

    tasks = {task.findtext("nme", ""): task for task in root.findall("Task")}
    for name, baseline_count in EXPECTED_TASK_ACTIONS.items():
        task = tasks.get(name)
        if task is None:
            findings.append(Finding("ERROR", "TASK_MISSING", name))
            continue
        actual = len(task.findall("Action"))
        if actual != baseline_count:
            findings.append(
                Finding("WARN", "ACTION_COUNT_CHANGED", f"{name}: baseline={baseline_count}, actual={actual}")
            )

    profiles = root.findall("Profile")
    if len(profiles) != 1:
        findings.append(Finding("ERROR", "PROFILE_COUNT", f"expected 1, found {len(profiles)}"))
    elif "LOG_SIGNIFICANT_PLACE_SAMPLE" in tasks:
        linked_id = profiles[0].findtext("mid0")
        task_id = tasks["LOG_SIGNIFICANT_PLACE_SAMPLE"].findtext("id")
        if linked_id != task_id:
            findings.append(Finding("ERROR", "PROFILE_LINK", f"mid0={linked_id}, task id={task_id}"))

    init = tasks.get("INIT_SIGNIFICANT_PLACES")
    if init is not None:
        conditions = {
            condition.findtext("lhs", "")
            for condition in init.findall("./Action/ConditionList/Condition")
        }
        for variable in ("%gl_latitude", "%gl_longitude"):
            if variable not in conditions:
                findings.append(Finding("ERROR", "INIT_COORDINATE_CHECK", f"missing condition for {variable}"))
        init_text = ET.tostring(init, encoding="unicode")
        if "%gl_coordinates_accuracy" not in init_text:
            findings.append(
                Finding("WARN", "INIT_ACCURACY_UNCHECKED", "daily initialization does not validate GPS accuracy")
            )

    load = tasks.get("LOAD_CONFIG_DEFAULTS")
    external = _load_external_config(config_path) if config_path else {}
    if load is not None and external:
        internal = _variable_sets(load)
        for key in ("MIN_STOP_MINUTES", "GPS_MAX_ACCURACY_METERS", "PLACE_RADIUS_METERS"):
            variable = f"%{key}"
            if variable in internal and key in external and internal[variable] != external[key]:
                findings.append(
                    Finding(
                        "WARN",
                        "FALLBACK_MISMATCH",
                        f"{key}: internal={internal[variable]}, external={external[key]}",
                    )
                )

    main = tasks.get("LOG_SIGNIFICANT_PLACE_SAMPLE")
    if main is not None:
        ordered = sorted(main.findall("Action"), key=lambda action: int(action.attrib["sr"].replace("act", "")))
        set_current = _first_action_index(ordered, "%CURRENT_PLACE_LAT")
        record_write = _first_csv_record_write_index(ordered)
        if set_current is not None and record_write is not None and set_current < record_write:
            findings.append(
                Finding("WARN", "STATE_BEFORE_WRITE", "confirmed-place state is updated before the CSV record write")
            )
        main_text = ET.tostring(main, encoding="unicode")
        if "lat &lt;" not in main_text and "lat <" not in main_text:
            findings.append(
                Finding("WARN", "GPS_RANGE_UNCHECKED", "main GPS validation does not enforce coordinate ranges")
            )
        if "%CANDIDATE_CONFIRM_COUNT" in main_text and not re.search(
            r"<lhs>%CANDIDATE_CONFIRM_COUNT</lhs>", main_text
        ):
            findings.append(
                Finding("WARN", "CONFIRM_COUNT_UNUSED", "candidate count is incremented but not used as a condition")
            )

    if not any(finding.level == "ERROR" for finding in findings):
        findings.append(Finding("OK", "STRUCTURE", "XML structure and required links are valid"))
    return findings


def _variable_sets(task: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for action in task.findall("Action"):
        if action.findtext("code") != "547":
            continue
        args = {node.attrib.get("sr"): node.text or "" for node in action.findall("Str")}
        if args.get("arg0", "").startswith("%"):
            result[args["arg0"]] = args.get("arg1", "")
    return result


def _load_external_config(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def _first_action_index(actions: list[ET.Element], variable: str) -> int | None:
    for index, action in enumerate(actions):
        if action.findtext("code") == "547" and action.findtext("Str[@sr='arg0']") == variable:
            return index
    return None


def _first_csv_record_write_index(actions: list[ET.Element]) -> int | None:
    for index, action in enumerate(actions):
        if action.findtext("code") != "410":
            continue
        value = action.findtext("Str[@sr='arg1']", "")
        if ";%CURRENT_PLACE_LAT;" in value:
            return index
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("xml", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()
    findings = validate(args.xml, args.config)
    for finding in findings:
        print(f"{finding.level:5} {finding.code}: {finding.message}")
    if any(finding.level == "ERROR" for finding in findings):
        return 1
    if args.strict and any(finding.level == "WARN" for finding in findings):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
