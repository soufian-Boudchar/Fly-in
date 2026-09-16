from src.classes.zone import Zone


class Connection:

    def __init__(self,
                 zone1: Zone,
                 zone2: Zone,
                 max_link_capacity: int = 1) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity
        self.active_drones: int = 0
