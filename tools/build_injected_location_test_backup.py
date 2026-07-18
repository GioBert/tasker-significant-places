#!/usr/bin/env python3
"""Build a private Tasker backup that injects a synthetic location for tests."""

from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path


TASK_NAME = "LOG_SIGNIFICANT_PLACE_SAMPLE"
TEST_LOG_DIR = "/storage/emulated/0/_SignificantPlaces/TestData/injected-B004"
SYNTHETIC_VALUES = (
    ("%gl_latitude", "0.000000"),
    ("%gl_longitude", "0.000000"),
    ("%gl_coordinates_accuracy", "3"),
)


def build(source: Path, destination: Path) -> None:
    tree = ET.parse(source)
    root = tree.getroot()
    task = next((item for item in root.findall("Task") if item.findtext("nme") == TASK_NAME), None)
    if task is None:
        raise ValueError(f"task not found: {TASK_NAME}")

    actions = sorted(task.findall("Action"), key=_action_index)
    if len(actions) != 85:
        raise ValueError(f"expected 85 B004 actions, found {len(actions)}")

    location_matches = [
        (index, action)
        for index, action in enumerate(actions)
        if action.findtext("code") == "366"
    ]
    if len(location_matches) != 1:
        raise ValueError(f"expected one Get Location v2 action, found {len(location_matches)}")
    location_index, _ = location_matches[0]

    template = next(
        (
            action
            for action in actions[location_index + 1 :]
            if action.findtext("code") == "547" and action.find("ConditionList") is None
        ),
        None,
    )
    if template is None:
        raise ValueError("unconditional Variable Set template not found")

    injected: list[ET.Element] = []
    for name, value in SYNTHETIC_VALUES:
        action = copy.deepcopy(template)
        _set_arg(action, "arg0", name)
        _set_arg(action, "arg1", value)
        injected.append(action)

    actions[location_index : location_index + 1] = injected
    _replace_actions(task, actions)
    _set_global(root, "%LOG_DIR", TEST_LOG_DIR)
    _set_global(root, "%MIN_STOP_MINUTES", "1")
    _verify(task, location_index)

    ET.indent(root, space="\t")
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def _verify(task: ET.Element, injection_index: int) -> None:
    actions = sorted(task.findall("Action"), key=_action_index)
    if len(actions) != 87:
        raise ValueError(f"expected 87 injected-test actions, found {len(actions)}")
    if any(action.findtext("code") == "366" for action in actions):
        raise ValueError("Get Location v2 is still enabled in the injected test")

    observed = [
        (_arg(action, "arg0"), _arg(action, "arg1"))
        for action in actions[injection_index : injection_index + len(SYNTHETIC_VALUES)]
    ]
    if observed != list(SYNTHETIC_VALUES):
        raise ValueError(f"unexpected injected actions: {observed!r}")

    write_index = next(
        (
            index
            for index, action in enumerate(actions)
            if action.findtext("code") == "410"
            and "%CANDIDATE_SINCE_TIMESTAMP;" in _arg(action, "arg1")
        ),
        None,
    )
    if write_index is None:
        raise ValueError("candidate CSV Write File action not found")

    for name in (
        "%PLACE_COUNTER",
        "%CURRENT_PLACE_ID",
        "%CURRENT_PLACE_NAME",
        "%CURRENT_PLACE_LAT",
        "%CURRENT_PLACE_LON",
    ):
        indexes = [
            index
            for index, action in enumerate(actions)
            if action.findtext("code") == "547" and _arg(action, "arg0") == name
        ]
        if len(indexes) != 1 or indexes[0] <= write_index:
            raise ValueError(f"global commit is not after Write File: {name}")


def _set_global(root: ET.Element, name: str, value: str) -> None:
    matches = [item for item in root.findall("Variable") if item.findtext("n") == name]
    if len(matches) != 1:
        raise ValueError(f"expected one global variable {name}, found {len(matches)}")
    node = matches[0].find("v")
    if node is None:
        raise ValueError(f"global variable has no value node: {name}")
    node.text = value


def _replace_actions(task: ET.Element, actions: list[ET.Element]) -> None:
    children = list(task)
    first_action = next(index for index, child in enumerate(children) if child.tag == "Action")
    for action in task.findall("Action"):
        task.remove(action)
    for offset, action in enumerate(actions):
        action.set("sr", f"act{offset}")
        task.insert(first_action + offset, action)


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
