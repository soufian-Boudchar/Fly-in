from src.classes import Zone, Connection
from src.graph import Graph

from typing import List, Dict


class Drone:
    """Represents an individual drone entity within the simulation.

    Attributes:
        drone_id (int): Unique numerical
        identifier for the drone.
        current_zone (str): Identifier name of the zone currently occupied.
        path (List[str]): Assigned sequence
        of zone names from start to end hub.
        zone_index (int): Current progress index
        along assigned path.
        wait_turns (int): Remaining delay turns during restricted zone transit.
        is_finished (bool): Flag indicating whether
        destination hub was reached.
        next_zone (str): Target zone name during pending multi-turn movements.
    """

    def __init__(self, drone_id: int) -> None:
        """Initializes Drone instance with specified numerical ID.

        Args:
            drone_id (int): Unique identifier for drone instance.
        """
        self.drone_id: int = drone_id
        self.current_zone: str = ""
        self.path: List[str] = []
        self.zone_index: int = 0
        self.wait_turns: int = 0
        self.is_finished: bool = False
        self.next_zone: str = ""


class Simulation:
    """Manages and executes turn-based drone routing and capacity enforcement.

    Attributes:
        graph (Graph): Network graph containing zone topologies and links.
        zones (Dict[str, Zone]): Direct lookup dictionary for graph zones.
        start_hub (str): Starting hub zone identifier.
        end_hub (str): Target destination hub zone identifier.
        nb_drones (int): Total count of drones participating in flight plan.
        paths (List[List[str]]): Pre-calculated route
        pathways distributed across drones.
        drones (List[Drone]): Active list of managed Drone objects.
        finished_drones (int): Number of drones that reached target hub.
        zone_usage (Dict[str | None, int]): Real-time
        occupancy tracker per zone.
        current_turn (int): Current turn step count in simulation.
        connections (List[Connection]): Complete list of network connections.
        conn_map (Dict[tuple[str | int, str | int], Connection]):
        Bidirectional lookup map for zone connection links.
    """

    def __init__(self,
                 graph: Graph,
                 nb_drones: int,
                 paths: List[List[str]]
                 ) -> None:
        """Initializes Simulation engine with graph, drone total, and path set.

        Args:
            graph (Graph): Spatial graph structure.
            nb_drones (int): Total number of drones to route.
            paths (List[List[str]]): Available route option sequences.
        """
        self.graph: Graph = graph
        self.zones: Dict[str, Zone] = graph.zones

        self.start_hub: str = graph.start_hub.name
        self.end_hub: str = graph.end_hub.name

        self.nb_drones: int = nb_drones

        self.paths: List[List[str]] = paths
        self.drones: List[Drone] = []
        self.finished_drones: int = 0
        self.zone_usage: Dict[str | None, int] = {}
        self.current_turn: int = 0

        self.connections: List[Connection] = graph.config.connections
        self.conn_map: Dict[tuple[str | int, str | int], Connection] = {}
        for conn in graph.config.connections:
            self.conn_map[(conn.zone1.name, conn.zone2.name)] = conn
            self.conn_map[(conn.zone2.name, conn.zone1.name)] = conn

    def init_simulation(self) -> None:
        """Resets simulation counters, occupancy state,
        and instantiates assigned drones."""
        self.finished_drones = 0
        self.current_turn = 0

        for zone in self.graph.zones.keys():
            self.zone_usage[zone] = 0

        for drone_id in range(1, self.nb_drones + 1):
            drone = Drone(drone_id)
            path_index = (drone_id - 1) % len(self.paths)

            drone.path = self.paths[path_index]
            drone.current_zone = self.start_hub
            drone.zone_index = 0
            drone.wait_turns = 0
            drone.is_finished = False
            self.drones.append(drone)

    def get_connection_capacity(self, zone1: str, zone2: str) -> Connection:
        """Looks up connection object linking
        specified pair of zones.

        Args:
            zone1 (str): Origin zone identifier.
            zone2 (str): Destination zone identifier.

        Returns:
            Connection: Connection object joining the two zones.
        """
        return self.conn_map[(zone1, zone2)]

    def can_move_to_zone(self, zone_name: str, conn: Connection) -> bool:
        """Checks if target zone and link have
        available capacity for drone entry.

        Args:
            zone_name (str): Target zone name.
            conn (Connection): Connecting link
            object to target zone.

        Returns:
            bool: True if movement constraints
            are satisfied, False otherwise.
        """
        if (zone_name == self.start_hub or zone_name == self.end_hub):
            return True

        zone_has_space = self.zone_usage[zone_name] < self.zones[
            zone_name].max_drones

        conn_has_space = True
        if conn is not None:
            conn_has_space = conn.active_drones < conn.max_link_capacity

        return conn_has_space and zone_has_space

    def process_single_turn(self) -> List[str]:
        """Processes single turn step movements,
        applying delays and capacity checks.

        Returns:
            List[str]: Formatted action move
            strings executed in current turn.
        """
        turn_moves = []
        for c in self.connections:
            c.active_drones = 0

        for drone in self.drones:
            if drone.wait_turns > 0 and drone.next_zone:
                conn = self.get_connection_capacity(drone.current_zone,
                                                    drone.next_zone)
                if conn:
                    conn.active_drones += 1

        self.drones.sort(key=lambda d: d.zone_index, reverse=True)

        for drone in self.drones:
            if drone.is_finished:
                continue

            if drone.current_zone == self.end_hub:
                drone.is_finished = True
                self.finished_drones += 1
                continue

            if drone.wait_turns > 0:
                drone.wait_turns -= 1
                if drone.wait_turns == 0:
                    drone.current_zone = drone.next_zone
                    drone.zone_index += 1
                    drone.next_zone = ""
                    turn_moves.append(
                        f"D{drone.drone_id}-{drone.current_zone}")

                    if drone.current_zone == self.end_hub:
                        drone.is_finished = True
                        self.finished_drones += 1
                continue
            next_zone = drone.path[drone.zone_index + 1]
            conn = self.get_connection_capacity(drone.current_zone, next_zone)

            if self.can_move_to_zone(next_zone, conn):

                if drone.current_zone != self.start_hub:
                    self.zone_usage[drone.current_zone] -= 1

                if next_zone != self.end_hub:
                    self.zone_usage[next_zone] += 1

                if conn is not None:
                    conn.active_drones += 1

                if self.zones[next_zone].type == "RESTRICTED":
                    drone.wait_turns = 1
                    drone.next_zone = next_zone

                    conn_name = f"{drone.current_zone}-{drone.next_zone}"
                    turn_moves.append(f"D{drone.drone_id}-{conn_name}")
                else:
                    drone.current_zone = next_zone
                    drone.zone_index += 1
                    turn_moves.append(f"D{drone.drone_id}-{next_zone}")

                    if drone.current_zone == self.end_hub:
                        drone.is_finished = True
                        self.finished_drones += 1
        return turn_moves

    def run(self) -> List[List[tuple[int, str]]]:
        """Executes complete simulation loop until
        all drones complete their route.

        Returns:
            List[List[tuple[int, str]]]:
            Turn-by-turn history log of drone movements.
        """
        self.init_simulation()
        history: List[List[tuple[int, str]]] = []

        while self.finished_drones < self.nb_drones:
            moves = self.process_single_turn()
            if moves:
                print(" ".join(moves))

                turn_history = []
                for m in moves:
                    parts = m.split('-')
                    drone_id = int(parts[0][1:])
                    target = "-".join(parts[1:])
                    turn_history.append((drone_id, target))

                history.append(turn_history)

            elif not moves and self.finished_drones < self.nb_drones:
                waiting = any(d.wait_turns > 0 for d in self.drones
                              if not d.is_finished)
                if not waiting:
                    continue

            if self.finished_drones == self.nb_drones:
                break
            self.current_turn += 1

        return history
