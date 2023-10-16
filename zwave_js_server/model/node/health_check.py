"""Provide a model for the Z-Wave JS node's health checks and power tests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from ...const import PowerLevel


class LifelineHealthCheckResultDataType(TypedDict, total=False):
    """Represent a lifeline health check result data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/Types.ts#L171
    latency: int  # required
    numNeighbors: int  # required
    failedPingsNode: int  # required
    rating: int  # required
    routeChanges: int
    minPowerlevel: int
    failedPingsController: int
    snrMargin: int


class LifelineHealthCheckSummaryDataType(TypedDict):
    """Represent a lifeline health check summary data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/_Types.ts#L254
    results: list[LifelineHealthCheckResultDataType]
    rating: int


@dataclass
class LifelineHealthCheckResult:
    """Represent a lifeline health check result."""

    data: LifelineHealthCheckResultDataType = field(repr=False)
    latency: int = field(init=False)
    num_neighbors: int = field(init=False)
    failed_pings_node: int = field(init=False)
    rating: int = field(init=False)
    route_changes: int | None = field(init=False)
    min_power_level: PowerLevel | None = field(init=False, default=None)
    failed_pings_controller: int | None = field(init=False)
    snr_margin: int | None = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.latency = self.data["latency"]
        self.num_neighbors = self.data["numNeighbors"]
        self.failed_pings_node = self.data["failedPingsNode"]
        self.rating = self.data["rating"]
        self.route_changes = self.data.get("routeChanges")
        if (min_power_level := self.data.get("minPowerlevel")) is not None:
            self.min_power_level = PowerLevel(min_power_level)
        self.failed_pings_controller = self.data.get("failedPingsController")
        self.snr_margin = self.data.get("snrMargin")


@dataclass
class LifelineHealthCheckSummary:
    """Represent a lifeline health check summary update."""

    data: LifelineHealthCheckSummaryDataType = field(repr=False)
    rating: int = field(init=False)
    results: list[LifelineHealthCheckResult] = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.rating = self.data["rating"]
        self.results = [
            LifelineHealthCheckResult(r) for r in self.data.get("results", [])
        ]


class RouteHealthCheckResultDataType(TypedDict, total=False):
    """Represent a route health check result data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/_Types.ts#L285
    numNeighbors: int  # required
    rating: int  # required
    failedPingsToTarget: int
    failedPingsToSource: int
    minPowerlevelSource: int
    minPowerlevelTarget: int


class RouteHealthCheckSummaryDataType(TypedDict):
    """Represent a route health check summary data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/_Types.ts#L317
    results: list[RouteHealthCheckResultDataType]
    rating: int


@dataclass
class RouteHealthCheckResult:
    """Represent a route health check result."""

    data: RouteHealthCheckResultDataType = field(repr=False)
    num_neighbors: int = field(init=False)
    rating: int = field(init=False)
    failed_pings_to_target: int | None = field(init=False)
    failed_pings_to_source: int | None = field(init=False)
    min_power_level_source: PowerLevel | None = field(init=False, default=None)
    min_power_level_target: PowerLevel | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.num_neighbors = self.data["numNeighbors"]
        self.rating = self.data["rating"]
        self.failed_pings_to_target = self.data.get("failedPingsToTarget")
        self.failed_pings_to_source = self.data.get("failedPingsToSource")
        if (min_power_level_source := self.data.get("minPowerlevelSource")) is not None:
            self.min_power_level_source = PowerLevel(min_power_level_source)
        if (min_power_level_target := self.data.get("minPowerlevelTarget")) is not None:
            self.min_power_level_target = PowerLevel(min_power_level_target)


@dataclass
class RouteHealthCheckSummary:
    """Represent a route health check summary update."""

    data: RouteHealthCheckSummaryDataType = field(repr=False)
    rating: int = field(init=False)
    results: list[RouteHealthCheckResult] = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.rating = self.data["rating"]
        self.results = [RouteHealthCheckResult(r) for r in self.data.get("results", [])]


@dataclass
class TestPowerLevelProgress:
    """Class to represent a test power level progress update."""

    acknowledged: int
    total: int


@dataclass
class CheckHealthProgress:
    """Represent a check lifeline/route health progress update."""

    rounds: int
    total_rounds: int
    last_rating: int
    last_result: LifelineHealthCheckResult | RouteHealthCheckResult
