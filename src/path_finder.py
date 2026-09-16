from src.graph import Graph
from src.classes import Zone, ZoneCost
from typing import Dict, List, Any
import heapq
from copy import deepcopy


class PathFinder:

    def __init__(self, graph: Graph):
        self.graph = graph
        self.zones = graph.zones
        self.start_hub = graph.start_hub.name
        self.end_hub = graph.end_hub.name

    def get_zone_cost(self, zone: Zone) -> Any:
        return ZoneCost[zone.type].value

    def recostruct_path(self, cam_from: Dict[str, str],
                        current: str) -> List[str]:
        path = []

        while current is not None:
            path.append(current)
            current = cam_from[current]

        path.reverse()
        return path

    def find_shortest_path(self, zones: Dict[str, Zone]) -> List[str] | None:
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
        zones_copy = deepcopy(self.zones)
        paths = []
        for _ in range(1):
            path = self.find_shortest_path(zones_copy)
            if path not in paths:
                paths.append(path)
            if path:
                for zone_name in path:
                    if (zone_name != self.start_hub
                            and zone_name != self.end_hub):
                        zones_copy[zone_name].type = "MASKED"
        if not paths[0]:
            exit(1)

        return paths
