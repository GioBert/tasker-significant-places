#!/usr/bin/env python3
"""Build B004: write a candidate record before committing global state."""

from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path


TASK_NAME = "LOG_SIGNIFICANT_PLACE_SAMPLE"
LOCAL_STAGE = {
    "%PLACE_COUNTER": ("%next_place_counter", "%PLACE_COUNTER + 1"),
    "%CURRENT_PLACE_ID": ("%next_place_id", "%next_place_counter"),
    "%CURRENT_PLACE_NAME": ("%next_place_name", "%PLACE_NAME_PREFIX%next_place_counter"),
    "%CURRENT_PLACE_LAT": ("%next_place_lat", "%CANDIDATE_PLACE_LAT"),
    "%CURRENT_PLACE_LON": ("%next_place_lon", "%CANDIDATE_PLACE_LON"),
}
GLOBAL_COMMIT = {
    "%PLACE_COUNTER": "%next_place_counter",
    "%CURRENT_PLACE_ID": "%next_place_id",
    "%CURRENT_PLACE_NAME": "%next_place_name",
    "%CURRENT_PLACE_LAT": "%next_place_lat",
    "%CURRENT_PLACE_LON": "%next_place_lon",
}


def build(source: Path, destination: Path) -> None:
    tree = ET.parse(source)
    root = tree.getroot()
    task = next((item for item in root.findall("Task") if item.findtext("nme") == TASK_NAME), None)
    if task is None:
        raise ValueError(f"task not found: {TASK_NAME}")

    actions = sorted(task.findall("Action"), key=_action_index)
    if any(
        action.findtext("code") == "547"
        and _arg(action, "arg0") == "%next_place_counter"
        for action in actions
    ):
        _verify(task)
        ET.indent(root, space="\t")
        destination.parent.mkdir(parents=True, exist_ok=True)
        tree.write(destination, encoding="utf-8", xml_declaration=True)
        return

    write_index = _find_record_write(actions)
    stage_actions: dict[str, ET.Element] = {}

    for global_name, (local_name, local_value) in LOCAL_STAGE.items():
        index, action = _find_variable_set(actions, global_name, before=write_index)
        _set_arg(action, "arg0", local_name)
        _set_arg(action, "arg1", local_value)
        stage_actions[global_name] = action
        if index >= write_index:
            raise ValueError(f"stage action occurs after write: {global_name}")

    known_places_script = _find_script(actions, "setGlobal('CURRENT_PLACE_NAME', bestName);")
    script = _arg(known_places_script, "arg0")
    replacements = {
        "global('CURRENT_PLACE_LAT')": "next_place_lat",
        "global('CURRENT_PLACE_LON')": "next_place_lon",
        "setGlobal('CURRENT_PLACE_NAME', bestName);": "next_place_name = bestName;",
    }
    for old, new in replacements.items():
        if old not in script:
            raise ValueError(f"expected JavaScript fragment not found: {old}")
        script = script.replace(old, new)
    _set_arg(known_places_script, "arg0", script)

    write_action = actions[write_index]
    record = _arg(write_action, "arg1")
    record_replacements = {
        "%CURRENT_PLACE_LAT": "%next_place_lat",
        "%CURRENT_PLACE_LON": "%next_place_lon",
        "%CURRENT_PLACE_ID": "%next_place_id",
        "%CURRENT_PLACE_NAME": "%next_place_name",
    }
    for old, new in record_replacements.items():
        if old not in record:
            raise ValueError(f"expected record field not found: {old}")
        record = record.replace(old, new)
    _set_arg(write_action, "arg1", record)

    commit_actions: list[ET.Element] = []
    for global_name, local_value in GLOBAL_COMMIT.items():
        action = copy.deepcopy(stage_actions[global_name])
        _set_arg(action, "arg0", global_name)
        _set_arg(action, "arg1", local_value)
        commit_actions.append(action)
    actions[write_index + 1 : write_index + 1] = commit_actions

    _replace_actions(task, actions)
    _verify(task)
    ET.indent(root, space="\t")
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def _verify(task: ET.Element) -> None:
    actions = sorted(task.findall("Action"), key=_action_index)
    if len(actions) != 85:
        raise ValueError(f"expected 85 actions after B004, found {len(actions)}")
    write_index = _find_record_write(actions)
    for global_name in GLOBAL_COMMIT:
        global_index, _ = _find_variable_set(actions, global_name)
        if global_index <= write_index:
            raise ValueError(f"global state still changes before record write: {global_name}")
    for local_name, _ in LOCAL_STAGE.values():
        local_index, _ = _find_variable_set(actions, local_name)
        if local_index >= write_index:
            raise ValueError(f"local stage occurs after record write: {local_name}")


def _replace_actions(task: ET.Element, actions: list[ET.Element]) -> None:
    children = list(task)
    first_action = next(index for index, child in enumerate(children) if child.tag == "Action")
    for action in task.findall("Action"):
        task.remove(action)
    for offset, action in enumerate(actions):
        action.set("sr", f"act{offset}")
        task.insert(first_action + offset, action)


def _find_record_write(actions: list[ET.Element]) -> int:
    matches = [
        index
        for index, action in enumerate(actions)
        if action.findtext("code") == "410" and "%CANDIDATE_SINCE_TIMESTAMP;" in _arg(action, "arg1")
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one candidate record write, found {len(matches)}")
    return matches[0]


def _find_variable_set(
    actions: list[ET.Element], variable: str, before: int | None = None
) -> tuple[int, ET.Element]:
    matches = [
        (index, action)
        for index, action in enumerate(actions)
        if action.findtext("code") == "547"
        and _arg(action, "arg0") == variable
        and (before is None or index < before)
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one Variable Set for {variable}, found {len(matches)}")
    return matches[0]


def _find_script(actions: list[ET.Element], fragment: str) -> ET.Element:
    matches = [
        action
        for action in actions
        if action.findtext("code") == "129" and fragment in _arg(action, "arg0")
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one JavaScriptlet containing {fragment!r}, found {len(matches)}")
    return matches[0]


def _arg(action: ET.Element, name: str) -> str:
    return action.findtext(f"Str[@sr='{name}']", "")


def _set_arg(action: ET.Element, name: str, value: str) -> None:
    node = action.find(f"Str[@sr='{name}']")
    if node is None:
        raise ValueError(f"missing {name} in action {action.get('sr')}")
    node.text = value


def _action_index(action: ET.Element) -> int:
    return int(action.attrib["sr"].removeprefix("act"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    build(args.source, args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
