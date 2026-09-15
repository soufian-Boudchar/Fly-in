from typing import List
from enum import Enum

class ZoneCost(Enum):
    PRIORITY = 0.5
    NORMAL = 1
    RESTRICTED = 2
    BLOCKED = float("inf")

class Zone:
    def __init__(self,
                 name: str,
                 x: int,
                 y: int,
                 zone_type="normal",
                 color: str = "none",
                 max_drones: int = 1) -> None:

        self.name = name
        self.x = x
        self.y = y
        self.type = zone_type.upper()
        self.color = color
        self.max_drones = max_drones
        self.current_drones: List[str] = []