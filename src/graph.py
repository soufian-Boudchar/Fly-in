from src.classes import Zone, Connection
from typing import Dict, List
from src.parsing.parser import ConfigParser


class Graph:
    """Manages the spatial network structure, adjacency lists,
    and zone connections.

    Attributes:
        config (ConfigParser): Configuration parser
        containing parsed network raw data.
        zones (Dict[str, Zone]): Mapping of zone
        names to Zone instances.
        adjacency_list (Dict[str | int, List[Connection]]): Map of zone
        names to incident connections.
        start_hub (Zone): Designated starting zone node.
        end_hub (Zone): Designated target destination zone node.
        nb_drones (int): Total number of drones to route through network.
    """

    def __init__(self, config: ConfigParser) -> None:
        """Initializes graph container with parsed configuration data.

        Args:
            config (ConfigParser): Validated parser instance
            containing raw map state.
        """
        self.config: ConfigParser = config
        self.zones: Dict[str, Zone] = config.zones

        self.adjacency_list: Dict[str | int, List[Connection]] = {}
        self.start_hub: Zone = config.start_hub
        self.end_hub: Zone = config.end_hub
        self.nb_drones: int = 0

    def add_adjacency(self, zone: Zone) -> None:
        """Ensures an entry for a given zone exists in the
        adjacency mapping.

        Args:
            zone (Zone): Zone instance to register.
        """
        if zone.name not in self.adjacency_list:
            self.adjacency_list[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        """Registers a bidirectional connection to both endpoint
        zones in adjacency list.

        Args:
            conn (Connection): Connection instance linking two zones.
        """
        self.adjacency_list[conn.zone1.name].append(conn)
        self.adjacency_list[conn.zone2.name].append(conn)

    def build_graph(self) -> None:
        """Populates graph network by linking all parsed zones
        and connection edges."""
        self.nb_drones = self.config.nb_drones

        for zone in self.zones.values():
            self.add_adjacency(zone)

        for conn in self.config.connections:
            self.add_connection(conn)

    def get_neighbors(self, zone_name: str) -> List[Zone]:
        """Retrieves all adjacent neighbor zones directly connected
        to target zone.

        Args:
            zone_name (str): Identifier name of queried zone.

        Returns:
            List[Zone]: List of neighboring Zone objects.
        """
        neighbors = []
        adj = self.adjacency_list.get(zone_name, [])
        for conn in adj:
            if zone_name == conn.zone1.name:
                neighbors.append(conn.zone2)
            else:
                neighbors.append(conn.zone1)

        return neighbors
