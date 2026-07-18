"""Pure-Python model of the Significant Places Tasker state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import asin, cos, isfinite, radians, sin, sqrt
from pathlib import Path
from typing import Iterable


CSV_HEADER = "TIMESTAMP;LAT;LON;PLACE_ID;NAME"


@dataclass(frozen=True)
class Config:
    place_radius_meters: float = 100.0
    min_stop_minutes: float = 5.0
    place_name_prefix: str = "Luogo_"
    gps_max_accuracy_meters: float = 50.0


@dataclass(frozen=True)
class KnownPlace:
    key: str
    display_name: str
    lat: float
    lon: float
    radius_meters: float


@dataclass(frozen=True)
class Sample:
    timestamp: datetime
    lat: float
    lon: float
    accuracy: float


@dataclass(frozen=True)
class Record:
    timestamp: datetime
    lat: float
    lon: float
    place_id: int
    name: str

    def to_csv(self) -> str:
        stamp = self.timestamp.strftime("%Y-%m-%d %H.%M")
        return f"{stamp};{self.lat:.7f};{self.lon:.7f};{self.place_id};{self.name}"


@dataclass
class State:
    log_date: str | None = None
    current_lat: float | None = None
    current_lon: float | None = None
    current_id: int = 0
    current_name: str = ""
    place_counter: int = 0
    candidate_lat: float | None = None
    candidate_lon: float | None = None
    candidate_since: datetime | None = None
    candidate_confirm_count: int = 0
    last_sample_time: datetime | None = None

    def reset_candidate(self) -> None:
        self.candidate_lat = None
        self.candidate_lon = None
        self.candidate_since = None
        self.candidate_confirm_count = 0


@dataclass
class StepResult:
    event: str
    record: Record | None = None
    details: dict[str, float | int | str] = field(default_factory=dict)


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * radius * asin(sqrt(a))


def load_config(path: Path) -> Config:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return Config(
        place_radius_meters=_positive(values.get("PLACE_RADIUS_METERS", "100"), "PLACE_RADIUS_METERS"),
        min_stop_minutes=_minimum(values.get("MIN_STOP_MINUTES", "5"), "MIN_STOP_MINUTES", 1),
        place_name_prefix=_nonempty(values.get("PLACE_NAME_PREFIX", "Luogo_"), "PLACE_NAME_PREFIX"),
        gps_max_accuracy_meters=_positive(
            values.get("GPS_MAX_ACCURACY_METERS", "50"), "GPS_MAX_ACCURACY_METERS"
        ),
    )


def load_known_places(path: Path | None) -> list[KnownPlace]:
    if path is None or not path.exists():
        return []
    result: list[KnownPlace] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("PLACE_KEY;"):
            continue
        parts = line.split(";")
        if len(parts) < 5:
            continue
        try:
            place = KnownPlace(parts[0].strip(), parts[1].strip(), float(parts[2]), float(parts[3]), float(parts[4]))
        except ValueError:
            continue
        if place.display_name and place.radius_meters > 0:
            result.append(place)
    return result


def load_samples(path: Path) -> list[Sample]:
    result: list[Sample] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("TIMESTAMP;"):
            continue
        parts = line.split(";")
        if len(parts) != 4:
            raise ValueError(f"{path}:{line_number}: expected 4 columns")
        result.append(Sample(datetime.fromisoformat(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])))
    return result


def load_records(path: Path) -> list[Record]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"{path}: empty CSV")
    if lines[0] != CSV_HEADER:
        raise ValueError(f"{path}: invalid header")

    result: list[Record] = []
    previous_timestamp: datetime | None = None
    for line_number, line in enumerate(lines[1:], 2):
        parts = line.split(";")
        if len(parts) != 5:
            raise ValueError(f"{path}:{line_number}: expected 5 columns")
        try:
            timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H.%M")
            lat = float(parts[1])
            lon = float(parts[2])
            place_id = int(parts[3])
        except ValueError as error:
            raise ValueError(f"{path}:{line_number}: invalid field") from error
        name = parts[4].strip()
        if timestamp.strftime("%Y-%m-%d %H.%M") != parts[0]:
            raise ValueError(f"{path}:{line_number}: invalid timestamp format")
        if previous_timestamp is not None and timestamp < previous_timestamp:
            raise ValueError(f"{path}:{line_number}: timestamps are not ordered")
        if not all(isfinite(value) for value in (lat, lon)) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"{path}:{line_number}: invalid coordinates")
        if place_id < 1:
            raise ValueError(f"{path}:{line_number}: invalid place id")
        if not name:
            raise ValueError(f"{path}:{line_number}: empty place name")
        result.append(Record(timestamp, lat, lon, place_id, name))
        previous_timestamp = timestamp
    return result


class SignificantPlacesSimulator:
    def __init__(self, config: Config, known_places: Iterable[KnownPlace] = ()) -> None:
        self.config = config
        self.known_places = list(known_places)
        self.state = State()
        self.records: list[Record] = []

    def process(self, sample: Sample) -> StepResult:
        if not self._valid_fix(sample):
            return StepResult("invalid_fix")

        day = sample.timestamp.date().isoformat()
        if self.state.log_date != day or self.state.current_lat is None or self.state.current_lon is None:
            return self._initialize_day(sample)

        distance_current = haversine_meters(
            sample.lat, sample.lon, self.state.current_lat, self.state.current_lon
        )
        self.state.last_sample_time = sample.timestamp
        if distance_current <= self.config.place_radius_meters:
            self.state.reset_candidate()
            return StepResult("same_place", details={"distance_current": distance_current})

        if self.state.candidate_since is None:
            self._start_candidate(sample)
            return StepResult("candidate_started", details={"distance_current": distance_current})

        assert self.state.candidate_lat is not None and self.state.candidate_lon is not None
        distance_candidate = haversine_meters(
            sample.lat, sample.lon, self.state.candidate_lat, self.state.candidate_lon
        )
        if distance_candidate > self.config.place_radius_meters:
            self._start_candidate(sample)
            return StepResult("candidate_replaced", details={"distance_candidate": distance_candidate})

        self.state.candidate_confirm_count += 1
        age_seconds = (sample.timestamp - self.state.candidate_since).total_seconds()
        if age_seconds < self.config.min_stop_minutes * 60:
            return StepResult(
                "candidate_waiting",
                details={"age_seconds": age_seconds, "confirm_count": self.state.candidate_confirm_count},
            )

        return self._confirm_candidate()

    def recover_from_records(self, records: Iterable[Record], day: str) -> bool:
        recovered = list(records)
        if not recovered:
            return False
        if any(record.timestamp.date().isoformat() != day for record in recovered):
            raise ValueError("daily recovery CSV contains records from another day")
        last = recovered[-1]
        self.records.extend(recovered)
        self.state = State(
            log_date=day,
            current_lat=last.lat,
            current_lon=last.lon,
            current_id=last.place_id,
            current_name=last.name,
            place_counter=max(record.place_id for record in recovered),
        )
        return True

    def _valid_fix(self, sample: Sample) -> bool:
        return (
            all(isfinite(value) for value in (sample.lat, sample.lon, sample.accuracy))
            and -90 <= sample.lat <= 90
            and -180 <= sample.lon <= 180
            and 0 <= sample.accuracy <= self.config.gps_max_accuracy_meters
        )

    def _initialize_day(self, sample: Sample) -> StepResult:
        self.state = State(
            log_date=sample.timestamp.date().isoformat(),
            current_lat=sample.lat,
            current_lon=sample.lon,
            current_id=1,
            current_name=self._name_for(sample.lat, sample.lon, 1),
            place_counter=1,
            last_sample_time=sample.timestamp,
        )
        record = Record(sample.timestamp, sample.lat, sample.lon, 1, self.state.current_name)
        self.records.append(record)
        return StepResult("day_initialized", record)

    def _start_candidate(self, sample: Sample) -> None:
        self.state.candidate_lat = sample.lat
        self.state.candidate_lon = sample.lon
        self.state.candidate_since = sample.timestamp
        self.state.candidate_confirm_count = 1

    def _confirm_candidate(self) -> StepResult:
        assert self.state.candidate_lat is not None
        assert self.state.candidate_lon is not None
        assert self.state.candidate_since is not None
        self.state.place_counter += 1
        self.state.current_id = self.state.place_counter
        self.state.current_lat = self.state.candidate_lat
        self.state.current_lon = self.state.candidate_lon
        self.state.current_name = self._name_for(
            self.state.current_lat, self.state.current_lon, self.state.current_id
        )
        record = Record(
            self.state.candidate_since,
            self.state.current_lat,
            self.state.current_lon,
            self.state.current_id,
            self.state.current_name,
        )
        self.records.append(record)
        self.state.reset_candidate()
        return StepResult("place_confirmed", record)

    def _name_for(self, lat: float, lon: float, place_id: int) -> str:
        matches: list[tuple[float, KnownPlace]] = []
        for place in self.known_places:
            distance = haversine_meters(lat, lon, place.lat, place.lon)
            if distance <= place.radius_meters:
                matches.append((distance, place))
        if matches:
            return min(matches, key=lambda item: item[0])[1].display_name
        return f"{self.config.place_name_prefix}{place_id}"


def _positive(value: str, name: str) -> float:
    number = float(value)
    if not isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be a positive number")
    return number


def _minimum(value: str, name: str, minimum: float) -> float:
    number = float(value)
    if not isfinite(number) or number < minimum:
        raise ValueError(f"{name} must be at least {minimum:g}")
    return number


def _nonempty(value: str, name: str) -> str:
    if not value:
        raise ValueError(f"{name} must not be empty")
    return value
