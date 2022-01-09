"""Provide a model for the Z-Wave JS node's health checks and power tests."""
from dataclasses import dataclass
from typing import List, Optional, TypedDict

from zwave_js_server.const import PowerLevel


class LifelineHealthCheckResultDataType(TypedDict, total=False):
    """Represent a lifeline health check result data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/Types.ts#L171
    latency: int  # required
    numNeighbors: int  # required
    failedPingsNode: int  # required
    routeChanges: int
    minPowerlevel: int
    failedPingsController: int
    snrMargin: int


class LifelineHealthCheckSummaryDataType(TypedDict):
    """Represent a lifeline health check summary data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/Types.ts#L211
    results: List[LifelineHealthCheckResultDataType]
    rating: int


class LifelineHealthCheckResult:
    """Represent a lifeline health check result."""

    def __init__(self, data: LifelineHealthCheckResultDataType) -> None:
        """Initialize lifeline health check result."""
        self.data = data

    @property
    def latency(self) -> int:
        """Return latency."""
        return self.data["latency"]

    @property
    def num_neighbors(self) -> int:
        """Return number of neighbors."""
        return self.data["numNeighbors"]

    @property
    def failed_pings_node(self) -> int:
        """Return number of failed pings to node."""
        return self.data["failedPingsNode"]

    @property
    def route_changes(self) -> Optional[int]:
        """Return number of route changes."""
        return self.data.get("routeChanges")

    @property
    def min_power_level(self) -> Optional[PowerLevel]:
        """Return minimum power level."""
        power_level = self.data.get("minPowerlevel")
        if power_level is not None:
            return PowerLevel(power_level)
        return None

    @property
    def failed_pings_controller(self) -> Optional[int]:
        """Return number of failed pings to controller."""
        return self.data.get("failedPingsController")

    @property
    def snr_margin(self) -> Optional[int]:
        """Return SNR margin."""
        return self.data.get("snrMargin")


class LifelineHealthCheckSummary:
    """Represent a lifeline health check summary update."""

    def __init__(self, data: LifelineHealthCheckSummaryDataType) -> None:
        """Initialize lifeline health check summary."""
        self._rating = data["rating"]
        self._results = [LifelineHealthCheckResult(r) for r in data.get("results", [])]

    @property
    def rating(self) -> int:
        """Return rating."""
        return self._rating

    @property
    def results(self) -> List[LifelineHealthCheckResult]:
        """Return lifeline health check results."""
        return self._results


class RouteHealthCheckResultDataType(TypedDict, total=False):
    """Represent a route health check result data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/Types.ts#L242
    numNeighbors: int  # required
    rating: int  # required
    failedPingsToTarget: int
    failedPingsToSource: int
    minPowerlevelSource: int
    minPowerlevelTarget: int


class RouteHealthCheckSummaryDataType(TypedDict):
    """Represent a route health check summary data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/Types.ts#L274
    results: List[RouteHealthCheckResultDataType]
    rating: int


class RouteHealthCheckResult:
    """Represent a route health check result."""

    def __init__(self, data: RouteHealthCheckResultDataType) -> None:
        """Initialize route health check result."""
        self.data = data

    @property
    def num_neighbors(self) -> int:
        """Return number of neighbors."""
        return self.data["numNeighbors"]

    @property
    def rating(self) -> int:
        """Return rating."""
        return self.data["rating"]

    @property
    def failed_pings_to_target(self) -> Optional[int]:
        """Return number of failed pings to target."""
        return self.data.get("failedPingsToTarget")

    @property
    def failed_pings_to_source(self) -> Optional[int]:
        """Return number of failed pings to source."""
        return self.data.get("failedPingsToSource")

    @property
    def min_power_level_source(self) -> Optional[PowerLevel]:
        """Return minimum power level source."""
        power_level = self.data.get("minPowerlevelSource")
        if power_level is not None:
            return PowerLevel(power_level)
        return None

    @property
    def min_power_level_target(self) -> Optional[PowerLevel]:
        """Return minimum power level target."""
        power_level = self.data.get("minPowerlevelTarget")
        if power_level is not None:
            return PowerLevel(power_level)
        return None


class RouteHealthCheckSummary:
    """Represent a route health check summary update."""

    def __init__(self, data: RouteHealthCheckSummaryDataType) -> None:
        """Initialize route health check summary."""
        self._rating = data["rating"]
        self._results = [RouteHealthCheckResult(r) for r in data.get("results", [])]

    @property
    def rating(self) -> int:
        """Return rating."""
        return self._rating

    @property
    def results(self) -> List[RouteHealthCheckResult]:
        """Return route health check results."""
        return self._results


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
