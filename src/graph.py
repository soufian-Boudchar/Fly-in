from src.classes import Zone, Connection
from typing import Dict, List
from src.parsing.parser import ConfigParser


class Graph:

    def __init__(self, config: ConfigParser):
        self.config: ConfigParser = config
        self.zones: Dict[str, Zone] = config.zones

        self.adjacency_list: Dict[str | int, List[Connection]] = {}
        self.start_hub: Zone = config.start_hub
        self.end_hub: Zone = config.end_hub
        self.nb_drones: int = 0

    def add_adjacency(self, zone: Zone) -> None:
        if zone.name not in self.adjacency_list:
            self.adjacency_list[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        self.adjacency_list[conn.zone1.name].append(conn)
        self.adjacency_list[conn.zone2.name].append(conn)

    def build_graph(self) -> None:
        self.nb_drones = self.config.nb_drones

        for zone in self.zones.values():
            self.add_adjacency(zone)

        for conn in self.config.connections:
            self.add_connection(conn)

    def get_neighbors(self, zone_name: str) -> List[Zone]:
        neighbors = []
        adj = self.adjacency_list.get(zone_name, [])
        for conn in adj:
            if zone_name == conn.zone1.name:
                neighbors.append(conn.zone2)
            else:
                neighbors.append(conn.zone1)

        return neighbors
