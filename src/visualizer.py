import pygame
import traceback


class Visualizer:

    def __init__(self, simulation):
        pygame.init()

        self.sim = simulation
        self.graph = simulation.graph

        self.width = 1280
        self.height = 720

        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.RESIZABLE
        )

        pygame.display.set_caption("Fly-in - Visualizer")

        # Pygame default fonts
        self.font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 32)

        self.calculate_bounds()

    def calculate_bounds(self):
        """Calculate the position and scale of the map."""

        if not self.graph.zones:
            self.scale = 1
            self.node_radius = 20
            self.offset_x = self.width // 2
            self.offset_y = self.height // 2
            return

        xs = [float(zone.x) for zone in self.graph.zones.values()]
        ys = [float(zone.y) for zone in self.graph.zones.values()]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        padding = 100

        usable_w = max(1, self.width - 2 * padding)
        usable_h = max(1, self.height - 2 * padding)

        dx = max_x - min_x
        dy = max_y - min_y

        # Avoid division by zero
        if dx == 0:
            dx = 1

        if dy == 0:
            dy = 1

        self.scale = min(
            usable_w / dx,
            usable_h / dy
        )

        # Keep node radius reasonable
        self.node_radius = max(
            15,
            min(30, int(self.scale / 3))
        )

        # Center the map
        self.offset_x = (
            padding
            + (usable_w - dx * self.scale) / 2
            - min_x * self.scale
        )

        self.offset_y = (
            padding
            + (usable_h - dy * self.scale) / 2
            - min_y * self.scale
        )

    def get_screen_pos(self, zone_name):
        """Convert map coordinates to screen coordinates."""

        zone = self.graph.zones[zone_name]

        x = float(zone.x)
        y = float(zone.y)

        screen_x = int(x * self.scale + self.offset_x)
        screen_y = int(y * self.scale + self.offset_y)

        return screen_x, screen_y

    def get_neighbor_name(self, neighbor):
        """
        Return the name of a neighbor.

        get_neighbors() may return either:
        - Zone objects
        - zone names (strings)
        """

        if isinstance(neighbor, str):
            return neighbor

        return neighbor.name

    def draw_connections(self):
        """Draw all graph connections."""

        drawn_links = set()

        for zone_name in self.graph.zones:

            neighbors = self.graph.get_neighbors(zone_name)

            pos1 = self.get_screen_pos(zone_name)

            for neighbor in neighbors:

                neighbor_name = self.get_neighbor_name(neighbor)

                if neighbor_name not in self.graph.zones:
                    continue

                # Same connection should only be drawn once
                link_id = tuple(
                    sorted((zone_name, neighbor_name))
                )

                if link_id in drawn_links:
                    continue

                pos2 = self.get_screen_pos(neighbor_name)

                pygame.draw.line(
                    self.screen,
                    (100, 100, 120),
                    pos1,
                    pos2,
                    3
                )

                drawn_links.add(link_id)

    def get_zone_color(self, zone_name, zone):
        """Return the color of a zone."""

        # Start and end
        if (
            zone_name == self.sim.start_hub
            or zone_name == self.sim.end_hub
        ):
            return (46, 204, 113)

        # Restricted
        if zone.type == "restricted":
            return (231, 76, 60)

        # Blocked
        if zone.type == "blocked":
            return (100, 100, 100)

        # Normal
        return (52, 152, 219)

    def draw_zones(self):
        """Draw all zones."""

        for zone_name, zone in self.graph.zones.items():

            pos = self.get_screen_pos(zone_name)

            color = self.get_zone_color(
                zone_name,
                zone
            )

            # Node
            pygame.draw.circle(
                self.screen,
                color,
                pos,
                self.node_radius
            )

            # Border
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                pos,
                self.node_radius,
                2
            )

            # Zone name
            text = self.font.render(
                zone_name,
                True,
                (255, 255, 255)
            )

            text_x = pos[0] - text.get_width() // 2
            text_y = pos[1] - self.node_radius - 25

            self.screen.blit(
                text,
                (text_x, text_y)
            )

    def draw_drones(self):
        """Draw drones currently inside zones."""

        drones_in_zones = {}

        for drone in self.sim.drones:

            if drone.is_finished:
                continue

            zone_name = drone.current_zone

            # If current_zone is a Zone object
            if not isinstance(zone_name, str):
                zone_name = zone_name.name

            if zone_name not in self.graph.zones:
                continue

            if zone_name not in drones_in_zones:
                drones_in_zones[zone_name] = []

            drones_in_zones[zone_name].append(
                drone.drone_id
            )

        # Draw drones
        for zone_name, drone_list in drones_in_zones.items():

            pos = self.get_screen_pos(zone_name)

            for i, drone_id in enumerate(drone_list):

                # Arrange drones around the node
                offset_x = (
                    pos[0]
                    - 10
                    + (i % 3) * 15
                )

                offset_y = (
                    pos[1]
                    - 10
                    + (i // 3) * 15
                )

                # Drone
                pygame.draw.circle(
                    self.screen,
                    (241, 196, 15),
                    (offset_x, offset_y),
                    10
                )

                # Drone border
                pygame.draw.circle(
                    self.screen,
                    (0, 0, 0),
                    (offset_x, offset_y),
                    10,
                    1
                )

                # Drone ID
                drone_text = self.font.render(
                    str(drone_id),
                    True,
                    (0, 0, 0)
                )

                text_x = (
                    offset_x
                    - drone_text.get_width() // 2
                )

                text_y = (
                    offset_y
                    - drone_text.get_height() // 2
                )

                self.screen.blit(
                    drone_text,
                    (text_x, text_y)
                )

    def draw_dashboard(self):
        """Draw simulation information."""

        turn_text = self.large_font.render(
            (
                f"Turn: {self.sim.current_turn} | "
                f"Finished: "
                f"{self.sim.finished_drones}/"
                f"{self.sim.nb_drones}"
            ),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            turn_text,
            (20, 20)
        )

        info_text = self.font.render(
            "SPACE = Next Turn | ESC = Quit",
            True,
            (180, 180, 180)
        )

        self.screen.blit(
            info_text,
            (20, 55)
        )

    def draw(self):
        """Draw the complete visualization."""

        # Background
        self.screen.fill((35, 35, 40))

        # 1. Connections
        self.draw_connections()

        # 2. Zones
        self.draw_zones()

        # 3. Drones
        self.draw_drones()

        # 4. Dashboard
        self.draw_dashboard()

        # Update screen
        pygame.display.flip()

    def handle_resize(self, event):
        """Handle window resizing."""

        self.width = max(400, event.w)
        self.height = max(300, event.h)

        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.RESIZABLE
        )

        self.calculate_bounds()

    def handle_key(self, event):
        """Handle keyboard input."""

        if event.key == pygame.K_ESCAPE:
            return False

        if event.key == pygame.K_SPACE:

            if self.sim.finished_drones < self.sim.nb_drones:

                moves = self.sim.process_single_turn()

                if moves:
                    print(
                        f"T{self.sim.current_turn} "
                        + " ".join(moves)
                    )

                self.sim.current_turn += 1

        return True

    def run_interactive(self):
        try:
            print("A: starting visualizer")

            print("B: initializing simulation")
            self.sim.init_simulation()
            print("C: simulation initialized")

            print("D: entering loop")

            running = True

            while running:
                self.draw()

                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        running = False

                    elif event.type == pygame.VIDEORESIZE:
                        self.width = event.w
                        self.height = event.h

                        self.screen = pygame.display.set_mode(
                            (self.width, self.height),
                            pygame.RESIZABLE
                        )

                        self.calculate_bounds()

                    elif event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_ESCAPE:
                            running = False

                        elif event.key == pygame.K_SPACE:

                            print("E: SPACE pressed")

                            if self.sim.finished_drones < self.sim.nb_drones:
                                moves = self.sim.process_single_turn()

                                print("F: process_single_turn finished")

                                if moves:
                                    print(
                                        f"T{self.sim.current_turn} "
                                        + " ".join(moves)
                                    )

                                self.sim.current_turn += 1

        except Exception:
            print("\n" + "=" * 60)
            print("VISUALIZER CRASH")
            print("=" * 60)

            traceback.print_exc()

            print("=" * 60)

        finally:
            pygame.quit()