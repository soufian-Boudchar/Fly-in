from enum import Enum


class ZoneCost(Enum):
    """Enumeration of turn movement costs for different zone types."""
    PRIORITY = 0.5
    NORMAL = 1
    RESTRICTED = 2
    MASKED = 20
    BLOCKED = float("inf")


class Zone:
    """Represents a node (zone) within the drone routing network.

    Attributes:
        name (str): Unique zone identifier.
        x (int | str): Abscissa coordinate of zone.
        y (int | str): Ordinate coordinate of zone.
        type (str): Uppercase zone type (e.g., NORMAL, RESTRICTED, BLOCKED).
        color (str): Terminal/GUI display color string.
        max_drones (int): Maximum simultaneous drone occupancy limit.
    """
    def __init__(self,
                 name: str,
                 x: int | str,
                 y: int | str,
                 zone_type: str = "normal",
                 color: str = "none",
                 max_drones: int = 1) -> None:
        """Initializes a Zone instance with coordinates and metadata.

        Args:
            name (str): Unique identifier for the zone.
            x (int | str): X-axis spatial coordinate.
            y (int | str): Y-axis spatial coordinate.
            zone_type (str, optional): Functional type of
            zone. Defaults to "normal".
            color (str, optional): Visual color attribute. Defaults to "none".
            max_drones (int, optional): Maximum
            drone capacity limit. Defaults to 1.
        """
        self.name = name
        self.x = x
        self.y = y
        self.type = zone_type.upper()
        self.color = color
        self.max_drones = max_drones
