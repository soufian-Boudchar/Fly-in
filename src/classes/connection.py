from src.classes.zone import Zone


class Connection:
    """Represents a bidirectional edge
    connecting two zones in the routing graph.

    Attributes:
        zone1 (Zone): The first endpoint zone.
        zone2 (Zone): The second endpoint zone.
        max_link_capacity (int): Maximum number of drones
        traversing link simultaneously.
        active_drones (int): Current count of drones
        actively crossing connection.
    """
    def __init__(self,
                 zone1: Zone,
                 zone2: Zone,
                 max_link_capacity: int = 1) -> None:
        """Initializes a Connection instance between two zones.

        Args:
            zone1 (Zone): First connected zone.
            zone2 (Zone): Second connected zone.
            max_link_capacity (int, optional): Maximum
            simultaneous drone capacity. Defaults to 1.
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity
        self.active_drones: int = 0
