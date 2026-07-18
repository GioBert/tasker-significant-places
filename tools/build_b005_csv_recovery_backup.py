#!/usr/bin/env python3
"""Build B005: recover Tasker state safely from an existing daily CSV."""

from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path


INIT_TASK = "INIT_SIGNIFICANT_PLACES"
MAIN_TASK = "LOG_SIGNIFICANT_PLACE_SAMPLE"
SCRIPT_MARKER = "B005_RECOVERY_V1"
RECOVERY_SCRIPT = r"""// B005_RECOVERY_V1
var raw = String(rec_raw || '').replace(/^\uFEFF/, '');
var lines = raw.split(/\r?\n/).map(function(line) {
  return String(line || '').trim();
}).filter(function(line) {
  return line.length > 0;
});
var expectedHeader = 'TIMESTAMP;LAT;LON;PLACE_ID;NAME';
var pathDateMatch = /(\d{4}-\d{2}-\d{2})-significant_places\.csv$/.exec(String(log_file || ''));
var expectedDate = pathDateMatch ? pathDateMatch[1] : '';
var previousTimestamp = '';
var maxId = 0;
var lastRecord = null;
var valid = true;
var errorCode = expectedDate ? 'empty_or_header' : 'path_date';

recovery_status = 'malformed';

function validTimestamp(value) {
  var match = /^(\d{4})-(\d{2})-(\d{2}) (\d{2})\.(\d{2})$/.exec(value);
  if (!match || value.substring(0, 10) !== expectedDate) return false;
  var y = Number(match[1]);
  var m = Number(match[2]);
  var d = Number(match[3]);
  var h = Number(match[4]);
  var min = Number(match[5]);
  var parsed = new Date(y, m - 1, d, h, min, 0, 0);
  return parsed.getFullYear() === y &&
         parsed.getMonth() === m - 1 &&
         parsed.getDate() === d &&
         parsed.getHours() === h &&
         parsed.getMinutes() === min;
}

if (expectedDate && lines.length === 1 && lines[0] === expectedHeader) {
  recovery_status = 'header_only';
  errorCode = '';
} else if (expectedDate && lines.length > 1 && lines[0] === expectedHeader) {
  for (var i = 1; i < lines.length; i++) {
    var parts = lines[i].split(';');
    if (parts.length !== 5) {
      valid = false;
      errorCode = 'fields';
      break;
    }
    var timestamp = String(parts[0] || '').trim();
    var lat = Number(parts[1]);
    var lon = Number(parts[2]);
    var idText = String(parts[3] || '').trim();
    var id = Number(idText);
    var name = String(parts[4] || '').trim();
    if (!validTimestamp(timestamp)) {
      valid = false;
      errorCode = 'timestamp';
      break;
    }
    if (previousTimestamp && timestamp < previousTimestamp) {
      valid = false;
      errorCode = 'order';
      break;
    }
    if (!isFinite(lat) || lat < -90 || lat > 90) {
      valid = false;
      errorCode = 'latitude';
      break;
    }
    if (!isFinite(lon) || lon < -180 || lon > 180) {
      valid = false;
      errorCode = 'longitude';
      break;
    }
    if (!/^[1-9]\d*$/.test(idText) || !isFinite(id)) {
      valid = false;
      errorCode = 'id';
      break;
    }
    if (!name) {
      valid = false;
      errorCode = 'name';
      break;
    }
    previousTimestamp = timestamp;
    maxId = Math.max(maxId, id);
    lastRecord = {lat: lat, lon: lon, id: id, name: name};
  }
  if (valid && lastRecord) {
    rec_lat = String(lastRecord.lat);
    rec_lon = String(lastRecord.lon);
    rec_id = String(lastRecord.id);
    rec_name = lastRecord.name;
    rec_counter = String(maxId);
    recovery_status = 'recovered';
    errorCode = '';
  }
}

rec_error = errorCode || 'none';

if (recovery_status === 'malformed') {
  var errorCount = parseInt(global('RECOVERY_ERROR_COUNT'), 10);
  if (!isFinite(errorCount) || errorCount < 0) errorCount = 0;
  setGlobal('RECOVERY_ERROR_COUNT', String(errorCount + 1));
  setGlobal('RECOVERY_STATUS', 'malformed');
  setGlobal('RECOVERY_LAST_ERROR', errorCode);
} else {
  setGlobal('RECOVERY_LAST_ERROR', '');
}"""


def build(source: Path, destination: Path) -> None:
    tree = ET.parse(source)
    root = tree.getroot()
    init = _task(root, INIT_TASK)
    main = _task(root, MAIN_TASK)
    actions = sorted(init.findall("Action"), key=_action_index)
    if any(SCRIPT_MARKER in _arg(action, "arg0") for action in actions):
        _upgrade_existing_recovery(actions)
        _verify(root)
        ET.indent(root, space="\t")
        destination.parent.mkdir(parents=True, exist_ok=True)
        tree.write(destination, encoding="utf-8", xml_declaration=True)
        return
    if len(actions) != 33:
        raise ValueError(f"expected 33 pre-B005 init actions, found {len(actions)}")
    if len(main.findall("Action")) != 85:
        raise ValueError("B004 main task must have 85 actions before B005")

    variable_template = next(
        action for action in actions if action.findtext("code") == "547"
    )
    test_template = _one(
        actions,
        "342",
        lambda action: _arg(action, "arg1") == "%log_file",
    )
    read_template = _one(actions, "417")
    script_template = _one(
        actions,
        "129",
        lambda action: "setGlobal('FIX_VALID'" in _arg(action, "arg0"),
    )
    if_template = _one(
        actions,
        "37",
        lambda action: action.findtext("ConditionList/Condition/lhs") == "%file_exists",
    )
    end_template = next(action for action in actions if action.findtext("code") == "38")
    main_actions = sorted(main.findall("Action"), key=_action_index)
    stop_template = _one(main_actions, "137")

    recovery_block = [
        _variable_set(variable_template, "%recovery_status", "unchecked"),
        _test_file(test_template, "%log_file", "%rec_type"),
        _if(if_template, "%rec_type", "", op="12"),
        _variable_set(variable_template, "%recovery_status", "malformed"),
        _read_file(read_template, "%log_file", "%rec_raw"),
        _variable_set(variable_template, "%rec_lat", "0"),
        _variable_set(variable_template, "%rec_lon", "0"),
        _variable_set(variable_template, "%rec_id", "0"),
        _variable_set(variable_template, "%rec_name", "__unset__"),
        _variable_set(variable_template, "%rec_counter", "0"),
        _variable_set(variable_template, "%rec_error", "js_not_completed"),
        _javascriptlet(script_template, RECOVERY_SCRIPT),
        _variable_set(variable_template, "%RECOVERY_LAST_ERROR", "%rec_error"),
        _if(if_template, "%recovery_status", "recovered"),
        _variable_set(variable_template, "%PLACE_COUNTER", "%rec_counter"),
        _variable_set(variable_template, "%CURRENT_PLACE_LAT", "%rec_lat"),
        _variable_set(variable_template, "%CURRENT_PLACE_LON", "%rec_lon"),
        _variable_set(variable_template, "%CURRENT_PLACE_ID", "%rec_id"),
        _variable_set(variable_template, "%CURRENT_PLACE_NAME", "%rec_name"),
        _variable_set(variable_template, "%CANDIDATE_PLACE_LAT", "0"),
        _variable_set(variable_template, "%CANDIDATE_PLACE_LON", "0"),
        _variable_set(variable_template, "%CANDIDATE_SINCE", "0"),
        _variable_set(variable_template, "%CANDIDATE_SINCE_TIMESTAMP", "0"),
        _variable_set(variable_template, "%CANDIDATE_CONFIRM_COUNT", "0"),
        _variable_set(variable_template, "%LAST_SAMPLE_TIME", "%TIMES"),
        _variable_set(variable_template, "%CURRENT_LOG_DATE", "%DATE"),
        _variable_set(variable_template, "%RECOVERY_STATUS", "recovered"),
        _stop(stop_template, with_error=False),
        copy.deepcopy(end_template),
        _if(if_template, "%recovery_status", "malformed"),
        _variable_set(variable_template, "%RECOVERY_STATUS", "malformed"),
        _stop(stop_template, with_error=True),
        copy.deepcopy(end_template),
        copy.deepcopy(end_template),
        _if(if_template, "%recovery_status", "unchecked"),
        _variable_set(variable_template, "%recovery_status", "new"),
        copy.deepcopy(end_template),
    ]

    directory_index = _index(actions, "409")
    actions[directory_index + 1 : directory_index + 1] = recovery_block
    _replace_initial_write_flow(
        actions,
        variable_template=variable_template,
        if_template=if_template,
        end_template=end_template,
        stop_template=stop_template,
    )

    _replace_actions(init, actions)
    _verify(root)
    ET.indent(root, space="\t")
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def _verify(root: ET.Element) -> None:
    init = _task(root, INIT_TASK)
    main = _task(root, MAIN_TASK)
    actions = sorted(init.findall("Action"), key=_action_index)
    if len(actions) != 82:
        raise ValueError(f"expected 82 B005 init actions, found {len(actions)}")
    if len(main.findall("Action")) != 85:
        raise ValueError("B005 changed the B004 main task")
    if any(action.findtext("code") == "43" for action in actions):
        raise ValueError("recovery task must not depend on Else")
    scripts = [action for action in actions if SCRIPT_MARKER in _arg(action, "arg0")]
    if len(scripts) != 1:
        raise ValueError(f"expected one B005 parser, found {len(scripts)}")
    if not all(
        fragment in _arg(scripts[0], "arg0")
        for fragment in ("maxId", "malformed", "header_only", "errorCode || 'none'")
    ):
        raise ValueError("B005 parser is incomplete")

    recovered_if = _if_index(actions, "%recovery_status", "recovered")
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
        index = _variable_index(actions, name, recovered_if, recovered_stop)
        if not recovered_if < index < recovered_stop:
            raise ValueError(f"recovery commit outside guarded block: {name}")

    malformed_if = _if_index(actions, "%recovery_status", "malformed")
    malformed_stop = next(
        action for action in actions[malformed_if + 1 :] if action.findtext("code") == "137"
    )
    if malformed_stop.find("Int[@sr='arg0']").get("val") != "1":
        raise ValueError("malformed CSV does not stop with error")

    new_if = _if_index(actions, "%recovery_status", "new")
    header_index = _write_index(actions, "TIMESTAMP;LAT;LON;PLACE_ID;NAME", new_if)
    new_record = _write_index(
        actions,
        "%timestamp;%CURRENT_PLACE_LAT;%CURRENT_PLACE_LON;%CURRENT_PLACE_ID;%CURRENT_PLACE_NAME",
        header_index,
    )
    new_status = next(
        index
        for index in range(new_record + 1, len(actions))
        if actions[index].findtext("code") == "547"
        and _arg(actions[index], "arg0") == "%RECOVERY_STATUS"
        and _arg(actions[index], "arg1") == "new"
    )
    if not new_if < header_index < new_record < new_status:
        raise ValueError("new-file writes are not guarded and ordered")

    header_only_if = _if_index(actions, "%recovery_status", "header_only")
    header_only_record = _write_index(
        actions,
        "%timestamp;%CURRENT_PLACE_LAT;%CURRENT_PLACE_LON;%CURRENT_PLACE_ID;%CURRENT_PLACE_NAME",
        header_only_if,
    )
    if header_only_record == new_record:
        raise ValueError("header-only initialization does not have its own record write")
    header_only_status = next(
        index
        for index in range(header_only_record + 1, len(actions))
        if actions[index].findtext("code") == "547"
        and _arg(actions[index], "arg0") == "%RECOVERY_STATUS"
        and _arg(actions[index], "arg1") == "header_only"
    )
    if not header_only_if < header_only_record < header_only_status:
        raise ValueError("header-only record write is not guarded and ordered")
    if _write_count(actions, "TIMESTAMP;LAT;LON;PLACE_ID;NAME") != 1:
        raise ValueError("header write must occur exactly once in the generated task")


def _upgrade_existing_recovery(actions: list[ET.Element]) -> None:
    scripts = [action for action in actions if SCRIPT_MARKER in _arg(action, "arg0")]
    if len(scripts) != 1:
        raise ValueError(f"expected one existing B005 parser, found {len(scripts)}")
    script = _arg(scripts[0], "arg0")
    if "errorCode || 'none'" in script:
        return
    old = "rec_error = errorCode;"
    if old not in script:
        raise ValueError("existing B005 parser has an unknown diagnostic format")
    _set_arg(scripts[0], "arg0", script.replace(old, "rec_error = errorCode || 'none';", 1))


def _replace_initial_write_flow(
    actions: list[ET.Element],
    *,
    variable_template: ET.Element,
    if_template: ET.Element,
    end_template: ET.Element,
    stop_template: ET.Element,
) -> None:
    header_index = next(
        index
        for index, action in enumerate(actions)
        if action.findtext("code") == "410" and _arg(action, "arg1") == "TIMESTAMP;LAT;LON;PLACE_ID;NAME"
    )
    record_index = _initial_record_index(actions)
    test_index = header_index - 2
    if (
        actions[test_index].findtext("code") != "342"
        or actions[header_index - 1].findtext("code") != "37"
        or record_index != header_index + 1
        or actions[record_index + 1].findtext("code") != "38"
    ):
        raise ValueError("unexpected pre-B005 header/record flow")
    test_file = actions[test_index]
    header = actions[header_index]
    record = actions[record_index]
    replacement = [
        test_file,
        _if(if_template, "%recovery_status", "new"),
        _if(if_template, "%file_exists", "", op="12"),
        _stop(stop_template, with_error=True),
        copy.deepcopy(end_template),
        header,
        record,
        _variable_set(variable_template, "%RECOVERY_STATUS", "new"),
        copy.deepcopy(end_template),
        _if(if_template, "%recovery_status", "header_only"),
        _if(if_template, "%file_exists", "", op="12"),
        copy.deepcopy(record),
        _variable_set(variable_template, "%RECOVERY_STATUS", "header_only"),
        _stop(stop_template, with_error=False),
        copy.deepcopy(end_template),
        _stop(stop_template, with_error=True),
        copy.deepcopy(end_template),
    ]
    actions[test_index : record_index + 2] = replacement


def _write_index(actions: list[ET.Element], value: str, start: int = 0) -> int:
    matches = [
        index
        for index in range(start, len(actions))
        if actions[index].findtext("code") == "410" and _arg(actions[index], "arg1") == value
    ]
    if not matches:
        raise ValueError(f"write not found after {start}: {value}")
    return matches[0]


def _write_count(actions: list[ET.Element], value: str) -> int:
    return sum(
        action.findtext("code") == "410" and _arg(action, "arg1") == value
        for action in actions
    )


def _initial_record_index(actions: list[ET.Element]) -> int:
    matches = [
        index
        for index, action in enumerate(actions)
        if action.findtext("code") == "410"
        and _arg(action, "arg1")
        == "%timestamp;%CURRENT_PLACE_LAT;%CURRENT_PLACE_LON;%CURRENT_PLACE_ID;%CURRENT_PLACE_NAME"
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one initial record write, found {len(matches)}")
    return matches[0]


def _variable_set(template: ET.Element, name: str, value: str) -> ET.Element:
    action = copy.deepcopy(template)
    _set_arg(action, "arg0", name)
    _set_arg(action, "arg1", value)
    maths = action.find("Int[@sr='arg3']")
    if maths is not None:
        maths.set("val", "0")
    return action


def _test_file(template: ET.Element, path: str, result: str) -> ET.Element:
    action = copy.deepcopy(template)
    _set_arg(action, "arg1", path)
    _set_arg(action, "arg2", result)
    return action


def _read_file(template: ET.Element, path: str, result: str) -> ET.Element:
    action = copy.deepcopy(template)
    _set_arg(action, "arg0", path)
    _set_arg(action, "arg1", result)
    return action


def _javascriptlet(template: ET.Element, script: str) -> ET.Element:
    action = copy.deepcopy(template)
    _set_arg(action, "arg0", script)
    return action


def _if(template: ET.Element, lhs: str, rhs: str, op: str = "2") -> ET.Element:
    action = copy.deepcopy(template)
    conditions = action.find("ConditionList")
    if conditions is None:
        raise ValueError("If template has no conditions")
    for condition in list(conditions.findall("Condition"))[1:]:
        conditions.remove(condition)
    condition = conditions.find("Condition")
    if condition is None:
        raise ValueError("If template has no condition")
    condition.find("lhs").text = lhs
    condition.find("op").text = op
    condition.find("rhs").text = rhs
    for boolean in list(conditions):
        if boolean.tag.startswith("bool"):
            conditions.remove(boolean)
    return action


def _stop(template: ET.Element, with_error: bool) -> ET.Element:
    action = copy.deepcopy(template)
    node = action.find("Int[@sr='arg0']")
    if node is None:
        raise ValueError("Stop template has no error flag")
    node.set("val", "1" if with_error else "0")
    return action


def _task(root: ET.Element, name: str) -> ET.Element:
    task = next((item for item in root.findall("Task") if item.findtext("nme") == name), None)
    if task is None:
        raise ValueError(f"task not found: {name}")
    return task


def _one(
    actions: list[ET.Element],
    code: str,
    predicate=lambda action: True,
) -> ET.Element:
    matches = [action for action in actions if action.findtext("code") == code and predicate(action)]
    if len(matches) != 1:
        raise ValueError(f"expected one action code {code}, found {len(matches)}")
    return matches[0]


def _index(actions: list[ET.Element], code: str) -> int:
    matches = [index for index, action in enumerate(actions) if action.findtext("code") == code]
    if len(matches) != 1:
        raise ValueError(f"expected one action code {code}, found {len(matches)}")
    return matches[0]


def _if_index(actions: list[ET.Element], lhs: str, rhs: str) -> int:
    matches = [
        index
        for index, action in enumerate(actions)
        if action.findtext("code") == "37"
        and action.findtext("ConditionList/Condition/lhs") == lhs
        and action.findtext("ConditionList/Condition/rhs") == rhs
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one If {lhs}={rhs}, found {len(matches)}")
    return matches[0]


def _variable_index(actions: list[ET.Element], name: str, start: int, end: int) -> int:
    matches = [
        index
        for index in range(start, end)
        if actions[index].findtext("code") == "547" and _arg(actions[index], "arg0") == name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one Variable Set {name}, found {len(matches)}")
    return matches[0]


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
