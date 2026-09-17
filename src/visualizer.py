import pygame
from typing import Dict, List, Tuple, Set, Any


class Visualizer:
    """Renders an interactive Pygame graphical interface for drone simulation.

    Attributes:
        sim (Any): Active simulation engine instance.
        graph (Any): Spatial graph structure containing zones and connections.
        width (int): Screen display width in pixels.
        height (int): Screen display height in pixels.
        screen (Any): Pygame display surface.
        font (pygame.font.Font): Primary small font for rendering labels.
        large_font (pygame.font.Font): Large font for status overlays.
        scale (float): Spatial scaling factor
        mapping graph coordinates to screen space.
        node_radius (int): Calculated rendering radius for zone node circles.
        offset_x (float): Screen X-axis offset for graph centering.
        offset_y (float): Screen Y-axis offset for graph centering.
    """

    def __init__(self, simulation: Any) -> None:
        """Initializes Pygame window and
        visualizer parameters using simulation state.

        Args:
            simulation (Any): Simulation engine instance containing graph data.
        """
        pygame.init()
        pygame.font.init()
        self.sim: Any = simulation
        self.graph: Any = simulation.graph

        self.width: int = 1280
        self.height: int = 720
        self.screen: Any = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Fly-in - Visualizer")

        self.font: pygame.font.Font = pygame.font.Font(None, 20)
        self.large_font: pygame.font.Font = pygame.font.Font(None, 32)

        self.scale: float = 1.0
        self.node_radius: int = 22
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.calculate_bounds()

    def calculate_bounds(self) -> None:
        """Calculates scaling factor and
        offsets to center graph nodes within viewport padding."""
        xs: List[float] = [float(zone.x) for zone in self.graph.zones.values()]
        ys: List[float] = [float(zone.y) for zone in self.graph.zones.values()]

        if not xs or not ys:
            self.scale = 1.0
            self.offset_x = self.width / 2.0
            self.offset_y = self.height / 2.0
            return

        min_x: float = min(xs)
        max_x: float = max(xs)
        min_y: float = min(ys)
        max_y: float = max(ys)

        padding: int = 100
        usable_w: float = float(self.width - 2 * padding)
        usable_h: float = float(self.height - 2 * padding)

        dx: float = (max_x - min_x) if max_x != min_x else 1.0
        dy: float = (max_y - min_y) if max_y != min_y else 1.0

        self.scale = min(usable_w / dx, usable_h / dy)
        self.node_radius = max(18, min(32, int(self.scale / 3)))

        self.offset_x = padding + (usable_w -
                                   dx * self.scale) / 2.0 - min_x * self.scale
        self.offset_y = padding + (usable_h -
                                   dy * self.scale) / 2.0 - min_y * self.scale

    def get_screen_pos(self, zone_name: str) -> Tuple[int, int]:
        """Transforms zone coordinates into screen pixel position.

        Args:
            zone_name (str): Identifier name of queried zone.

        Returns:
            Tuple[int, int]: Transformed screen coordinates (x, y).
        """
        zone: Any = self.graph.zones[zone_name]
        return (int(float(zone.x) * self.scale + self.offset_x),
                int(float(zone.y) * self.scale + self.offset_y))

    def draw(self) -> None:
        """Renders complete visualization frame
        including edges, nodes, drones, and UI overlay."""
        self.screen.fill((30, 32, 38))

        drawn_conns: Set[str] = set()
        for conn in getattr(self.graph.config, 'connections', []):
            z1_name = str(conn.zone1.name)
            z2_name = str(conn.zone2.name)
            conn_key = "-".join(sorted([z1_name, z2_name]))

            if conn_key in drawn_conns:
                continue
            drawn_conns.add(conn_key)

            if z1_name in self.graph.zones and z2_name in self.graph.zones:
                p1 = self.get_screen_pos(z1_name)
                p2 = self.get_screen_pos(z2_name)

                active = getattr(conn, 'active_drones', 0)
                max_cap = getattr(conn, 'max_link_capacity', 1)

                line_color = (231, 76,
                              60) if active >= max_cap and max_cap > 0 else (
                                  100, 110, 130)
                line_width = 4 if active > 0 else 2

                pygame.draw.line(self.screen, line_color, p1, p2, line_width)

                mid_x = (p1[0] + p2[0]) // 2
                mid_y = (p1[1] + p2[1]) // 2
                if max_cap < 99999:
                    txt_sf = self.font.render(f"c:{active}/{max_cap}", True,
                                              (200, 200, 200))
                    rect = txt_sf.get_rect(center=(mid_x, mid_y))
                    pygame.draw.rect(self.screen, (20, 22, 28),
                                     rect.inflate(6, 4))
                    self.screen.blit(txt_sf, rect)

        for zone_name, zone in self.graph.zones.items():
            pos = self.get_screen_pos(str(zone_name))
            z_type = getattr(zone, 'type', 'NORMAL').upper()
            max_drones = getattr(zone, 'max_drones', 1)

            if zone_name == self.sim.start_hub:
                color = (46, 204, 113)
            elif zone_name == self.sim.end_hub:
                color = (155, 89, 182)
            elif z_type == "RESTRICTED":
                color = (231, 76, 60)
            elif z_type == "BLOCKED":
                color = (100, 100, 100)
            else:
                color = (52, 152, 219)

            pygame.draw.circle(self.screen, color, pos, self.node_radius)
            pygame.draw.circle(self.screen, (255, 255, 255), pos,
                               self.node_radius, 2)

            if zone_name == self.sim.start_hub:
                name_str = f"START: {zone_name}"
            else:
                if zone_name == self.sim.end_hub:
                    name_str = f"END: {zone_name}"
                else:
                    name_str = str(zone_name)

            text = self.font.render(name_str, True, (255, 255, 255))
            self.screen.blit(text, (pos[0] - text.get_width() // 2,
                                    pos[1] - self.node_radius - 22))

            if zone_name not in (self.sim.start_hub, self.sim.end_hub):
                occ = self.sim.zone_usage.get(zone_name, 0)
                occ_sf = self.font.render(f"{occ}/{max_drones}", True,
                                          (255, 240, 180))
                self.screen.blit(occ_sf, (pos[0] - occ_sf.get_width() // 2,
                                          pos[1] + self.node_radius + 4))

        drones_in_loc: Dict[str, List[int]] = {}
        for drone in self.sim.drones:
            if getattr(drone, 'is_finished', False):
                drones_in_loc.setdefault(str(self.sim.end_hub),
                                         []).append(drone.drone_id)
            else:
                c_zone = getattr(drone, 'current_zone', self.sim.start_hub)
                n_zone = getattr(drone, 'next_zone', "")
                w_turns = getattr(drone, 'wait_turns', 0)

                if w_turns > 0 and n_zone:
                    loc_key = f"{c_zone}-{n_zone}"
                else:
                    loc_key = str(c_zone)
                drones_in_loc.setdefault(loc_key, []).append(drone.drone_id)

        for loc_key, d_list in drones_in_loc.items():
            if "-" in loc_key and loc_key not in self.graph.zones:
                z1, z2 = loc_key.split("-")
                if z1 in self.graph.zones and z2 in self.graph.zones:
                    p1 = self.get_screen_pos(z1)
                    p2 = self.get_screen_pos(z2)
                    base_pos = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
                else:
                    continue
            else:
                if loc_key in self.graph.zones:
                    base_pos = self.get_screen_pos(loc_key)
                else:
                    continue

            for idx, d_id in enumerate(d_list):
                row = idx // 4
                col = idx % 4

                ox = base_pos[0] + (col * 18) - 27
                oy = base_pos[1] + (row * 18) - (15 if "-" in loc_key else 10)

                pygame.draw.circle(self.screen, (241, 196, 15), (ox, oy), 9)
                pygame.draw.circle(self.screen, (0, 0, 0), (ox, oy), 9, 1)
                dtxt = self.font.render(str(d_id), True, (0, 0, 0))
                self.screen.blit(
                    dtxt,
                    (ox - dtxt.get_width() // 2, oy - dtxt.get_height() // 2))

        fin = getattr(self.sim, 'finished_drones', 0)
        tot = getattr(self.sim, 'nb_drones', len(self.sim.drones))
        turn = getattr(self.sim, 'current_turn', 1)

        self.screen.blit(
            self.large_font.render(f"Turn: {turn} | Finished: {fin}/{tot}",
                                   True, (255, 255, 255)), (20, 20))
        self.screen.blit(
            self.font.render("SPACE: Single Step | ESC: Quit", True,
                             (170, 170, 170)), (20, 58))

        pygame.display.flip()

    def run_interactive(self) -> None:
        """Executes interactive Pygame event loop
        for window events and manual turn progression."""
        if hasattr(self.sim, 'init_simulation'):
            self.sim.init_simulation()

        running = True
        clock = pygame.time.Clock()

        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.RESIZABLE)
                    self.calculate_bounds()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.sim.finished_drones < self.sim.nb_drones:
                            moves = self.sim.process_single_turn()
                            if moves:
                                print(" ".join(moves))
                            if not moves:
                                exit(0)
                            self.sim.current_turn += 1
            clock.tick(60)

        pygame.quit()
