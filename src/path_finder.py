from src.graph import Graph
from src.classes import Zone, ZoneCost
from typing import Dict, List, Any
import heapq
from copy import deepcopy


class PathFinder:
    """Computes optimal collision-free path routes for drones
    across graph network.

    Uses priority-queue pathfinding with zone masking to extract
    multiple disjoint paths between start and end hubs.

    Attributes:
        graph (Graph): Routing graph instance.
        zones (Dict[str, Zone]): Reference map of graph zone objects.
        start_hub (str): Starting hub zone identifier.
        end_hub (str): Target destination hub zone identifier.
    """

    def __init__(self, graph: Graph) -> None:
        """Initializes PathFinder with target graph state.

        Args:
            graph (Graph): Graph instance containing network topology.
        """
        self.graph = graph
        self.zones = graph.zones
        self.start_hub = graph.start_hub.name
        self.end_hub = graph.end_hub.name

    def get_zone_cost(self, zone: Zone) -> Any:
        """Retrieves numerical traversal turn cost associated
        with zone type.

        Args:
            zone (Zone): Evaluated zone instance.

        Returns:
            Any: Traversal cost value defined in ZoneCost enum.
        """
        return ZoneCost[zone.type].value

    def recostruct_path(self, cam_from: Dict[str, str],
                        current: str) -> List[str]:
        """Reconstructs ordered path node list from parent
        traversal tracking map.

        Args:
            cam_from (Dict[str, str]): Mapping of child zone
            names to parent zone names.
            current (str): Target destination zone name.

        Returns:
            List[str]: Ordered sequence of zone names from
            start to end hub.
        """
        path = []

        while current is not None:
            path.append(current)
            current = cam_from[current]

        path.reverse()
        return path

    def find_shortest_path(self, zones: Dict[str, Zone]) -> List[str] | None:
        """Calculates single shortest path from start to end
        hub using priority queue Dijkstra algorithm.

        Args:
            zones (Dict[str, Zone]): Working dictionary of zone states.

        Returns:
            List[str] | None: Ordered sequence of zone node
            names if path exists, else None.
        """
        distances = {}

        for zone_name in zones:
            distances[zone_name] = float("inf")

        distances[self.start_hub] = 0

        cam_from: Dict[str, Any] = {self.start_hub: None}
        pq = [(0, self.start_hub)]

        while pq:
            cost, current = heapq.heappop(pq)

            if current == self.end_hub:
                return self.recostruct_path(cam_from, current)

            if cost > distances[current]:
                continue

            neigh = self.graph.get_neighbors(current)

            for n in neigh:
                neighbor = zones[n.name]

                best_cost = cost + self.get_zone_cost(neighbor)

                if best_cost < distances[neighbor.name]:
                    distances[neighbor.name] = best_cost
                    cam_from[neighbor.name] = current

                    heapq.heappush(pq, (best_cost, neighbor.name))

        return None

    def get_path(self) -> Any:
        """Discovers multiple path routes by iteratively
        masking used zones.

        Returns:
            Any: List of discovered path routes containing zone name sequences.

        Raises:
            ValueError: If no viable path exists from start
            to end hub.
        """
        zones_copy = deepcopy(self.zones)
        paths = []
        for _ in range(2):
            path = self.find_shortest_path(zones_copy)
            if path not in paths:
                paths.append(path)
            if path:
                for zone_name in path:
                    if (zone_name != self.start_hub
                            and zone_name != self.end_hub):
                        zones_copy[zone_name].type = "MASKED"
        if not paths[0]:
            raise ValueError("\033[31m[ERROR]\033[0m No path found!")

        return paths
