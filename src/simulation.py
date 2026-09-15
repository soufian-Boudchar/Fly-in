from .classes import Zone, Connection, ZoneCost
from .graph import Graph
from .path_finder import PathFinder
from typing import List, Dict




class Drone:
    def __init__(self, drone_id: int):
        self.drone_id = drone_id
        self.current_zone: Zone | None= None
        self.path = None
        self.path_index = 0
        self.wait_turns = 0
        self.is_finished = False

class Simulation:
    def __init__(self, graph: Graph, nb_drones: int, path: List[str]):
        self.graph = graph
        self.zones = graph.zones
        
        self.start_hub = graph.start_hub.name
        self.end_hub = graph.end_hub.name

        self.nb_drones = nb_drones
        self.path = path
        self.drones = []
        self.finished_drones = 0
        self.zone_occupancy: Dict[str, int] = {}
        self.current_turn = 1
        
    def init_simulation(self):
            self.drones = []
            self.finished_drones = 0
            self.current_turn = 1
            
            for zone in self.graph.zones.keys():
                self.zone_occupancy[zone] = 0
                
            for drone_id in range(1, self.nb_drones + 1):
                drone = Drone(drone_id)
                drone.path = self.path
                drone.current_zone = self.start_hub
                drone.path_index = 0
                drone.wait_turns = 0
                drone.is_finished = False
                self.drones.append(drone)
            
    
    def can_move_to_zone(self, zone_name: str) -> bool:
        if (zone_name == self.start_hub or
            zone_name == self.end_hub
            ):
            return True
        
        if self.zone_occupancy[zone_name] < self.zones[zone_name].max_drones:
            return True
        return False
        
    
    def process_single_turn(self) -> List[str]:
        turn_moves = []
        
        
        self.drones.sort(key=lambda d: d.path_index, reverse=True)
        
        for drone in self.drones:
            
            if drone.is_finished:
                continue
            
            if drone.current_zone == self.end_hub:
                drone.is_finished = True
                self.finished_drones += 1
                continue

            if drone.wait_turns > 0:
                drone.wait_turns -= 1
                continue
            
            next_zone = self.path[drone.path_index + 1]
            
            if self.can_move_to_zone(next_zone):
                if drone.current_zone != self.start_hub:
                   self.zone_occupancy[drone.current_zone] -= 1
                   
                if next_zone != self.end_hub:
                    self.zone_occupancy[next_zone] += 1
                    
                drone.current_zone = next_zone
                drone.path_index += 1
                if self.zones[next_zone].type == "RESTRICTED":
                    drone.wait_turns = 1

                turn_moves.append(f"D{drone.drone_id}-{next_zone}")
                
        return turn_moves


    def run(self):
        self.init_simulation()
        
        while self.finished_drones < self.nb_drones:
            moves = self.process_single_turn()
            
                
            if moves:
                print(f"T{self.current_turn} " + " ".join(moves))
            # elif not moves and self.finished_drones < self.nb_drones:
            #     waiting = any(d.wait_turns > 0 for d in self.drones if not d.is_finished)
            #     if not waiting:
            #         continue
            
            if self.finished_drones == self.nb_drones:
                break
            self.current_turn += 1