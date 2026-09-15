from .graph import Graph
from .classes import  Zone, ZoneCost
from typing import Dict, List, Any
import heapq

class PathFinder:   
    def __init__(self, graph: Graph):
        self.graph = graph
        self.zones = graph.zones
        self.start_hub = graph.start_hub.name
        self.end_hub = graph.end_hub.name

    def get_zone_cost(self, zone: Zone):
        return ZoneCost[zone.type].value
    
    
    def recostruct_path(self, cam_from: Dict[str, str], current: str):
        path = []
        
        while current is not None:
            path.append(current)
            current = cam_from[current]
        
        path.reverse()
        return path


    def find_shortest_path(self):
        distances = {}

        for zone_name in self.zones.keys():
            distances[zone_name] = float("inf")

        distances[self.start_hub] = 0

        cam_from = {self.start_hub: None}
        pq = [(0, self.start_hub)]


        while pq:
            cost, current = heapq.heappop(pq)
            if current == self.end_hub:
                return self.recostruct_path(cam_from, current)


            if cost > distances[current]:
                continue

            neighbors = self.graph.get_neighbors(current)
            for neighbor in neighbors:
                best_cost = self.get_zone_cost(neighbor) + cost

                if best_cost < distances[neighbor.name]:
                    distances[neighbor.name] = best_cost
                    cam_from[neighbor.name] = current
                    
                    heapq.heappush(pq, (best_cost, neighbor.name))
        return None
