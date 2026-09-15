import os
import sys
from typing import List, Dict, Optional
import re
from collections import Counter
from ..classes import Zone, Connection


class ConfigParser:

    def __init__(self, argv: str) -> None:
        self.argv = argv
        self.nb_drones = 0
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None
        self.current_mode: None | str = None
        self.finished_keys = {
            "nb_drones": False,
            "start_hub": False,
            "hub": False,
            "end_hub": False,
            "connection": False
        }

    @property
    def get_file_content_lines(self):
        try:
            with open(self.argv[1], "r") as file:
                content = file.read()
                if not content.strip():
                    raise ValueError("\033[31m[ERROR]\033[0m The file is empty!")
        except IndexError:
            raise ValueError(f"\033[31m[ERROR]\033[0m File not found!")
        content = content.splitlines()
        content.append("EOF")
        return content

    @property
    def check_order(self) -> int:
        order = 1
        for key, finished in self.finished_keys.items():
            if not finished:
                continue
            if key == "nb_drones" and order != 1:
                return -1
            elif key == "connection" and not order == 5:
                return -1
            order += 1
        return 0

    def char_counter(self, line: str, char: str):
        count = 0
        for i in line:
            if i == char:
                count += 1
        return count

    def mode_selecter(self, line: str) -> str | int:
        if re.match(r"^nb_drones\s*:",
                    line) and not self.finished_keys['nb_drones']:
            return "nb_drones"

        elif re.match(r"^start_hub\s*:",
                      line) and not self.finished_keys['start_hub']:
            return "start_hub"

        elif re.match(r"^hub\s*:", line) and not self.finished_keys['hub']:
            return "hub"

        elif re.match(r"^end_hub\s*:",
                      line) and not self.finished_keys['end_hub']:
            return "end_hub"

        elif re.match(r"^connection\s*:",
                      line) and not self.finished_keys['connection']:
            return "connection"

        elif line == 'EOF':
            return "EOF"
        else:
            return -1

    def substring_between(self, line: str, start, end):
        if isinstance(start, str):
            i_start = line.index(start[-1])
        elif isinstance(start, int):
            i_start = start

        if isinstance(end, str):
            i_end = line.index(end[-1])
        elif isinstance(end, int):
            i_end = end

        return line[i_start + 1:i_end]

    def zone_validator(self, zone: str):
        valid_types = ["normal", "blocked", "restricted", "priority"]
        if zone not in valid_types:
            return -5
        return 0



    def get_nb_drones(self, line: str) -> int:
        # return -1: duplicate nb_drones
        # return -2: invalid nb_drones syntax
        # return -3: invalid nb_drones value
        if self.finished_keys['nb_drones']:
            return -1

        res = re.split(r"[: \t]+", line)
        if len(res) != 2:
            return -2
        try:
            if int(res[1]) <= 0:
                return -3
            return int(res[1])
        except ValueError:
            return -3

    def get_hub(self, line: str) -> Zone | int:

        if not self.finished_keys['nb_drones']:
            return -1
        metadata = {"zone": "normal", "color": "none", "max_drones": 1}
        hub_info = {}

        if '[' in line or ']' in line:
            if not (self.char_counter(line, '[') == 1
                    and self.char_counter(line, ']') == 1):
                return -3
            # get metadata from line
            variables = self.substring_between(line, '[', ']').split()
            # check if string has more '=' chars
            if self.char_counter(line, '=') != len(variables):
                return -3

            # check if string has no '='
            for var in variables:
                if '=' not in var or '#' in var:
                    return -3
                key, value = var.split('=')

                if key not in metadata:
                    return -4
                elif not value:
                    return -5

                metadata[key] = value
            try:
                metadata['max_drones'] = int(metadata['max_drones'])
                if metadata['max_drones'] <= 0:
                    raise ValueError
            except ValueError:
                return -5
        if '[' in line:
            data = self.substring_between(line, 'hub:', '[').split()
        else:
            data = self.substring_between(line, "hub:", len(line)).split()

        if len(data) != 3:
            return -2

        if '-' in data[0]:
            return -7

        hub_info['name'] = data[0]

        try:
            hub_info['x'] = int(data[1])
        except ValueError:
            return -6
        try:
            hub_info['y'] = int(data[2])
        except ValueError:
            return -6

        if self.zone_validator(metadata['zone']) == -5:
            return -5
        zone = Zone(hub_info['name'], hub_info['x'], hub_info['y'],
                    metadata['zone'], metadata['color'],
                    metadata['max_drones'])

        return zone

    def get_connection(self, line: str):

        # return -1: duplicate start_hub
        # return -3: invalid metadata syntax
        # return -4: invalid metadata key
        # return -5: invalid metadata value
        # retrun -8: invalid zone name
        # return -9: invalid connection syntax
        if self.finished_keys['connection']:
            return -1
        metadata = {'max_link_capacity': 1}

        if '[' in line or ']' in line:
            if not (self.char_counter(line, '[') == 1
                    and self.char_counter(line, ']') == 1):

                return -3
            # get metadata from line
            variables = self.substring_between(line, '[', ']').split()
            # check if string has more '=' chars
            if self.char_counter(line, '=') != len(variables):
                return -3

            # check if string has no '='
            for var in variables:
                if '=' not in var or '#' in var:
                    return -3
                key, value = var.split('=')

                if key not in metadata:
                    return -4
                elif not value:
                    return -5

                metadata[key] = value
            try:
                metadata['max_link_capacity'] = int(
                    metadata['max_link_capacity'])
                if metadata['max_link_capacity'] <= 0:
                    raise ValueError
            except ValueError:
                return -5

        if '[' in line:
            data = self.substring_between(line, 'connection:', '[').split()
        else:
            data = self.substring_between(line, "connection:",
                                          len(line)).split()
        if len(data) != 1:
            return -9

        zone1_name, zone2_name = data[0].split('-')

        try:

            zone1 = self.zones[zone1_name]
            zone2 = self.zones[zone2_name]
        except KeyError:
            return -8

        return Connection(zone1, zone2, metadata['max_link_capacity'])

    def error_raiser(self, line_num: int, error_num: int):
        if error_num == -1:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Unexpected or duplicate key."
            )
        elif error_num == -2:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid hub format!")
        elif error_num == -3:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid metadata syntax!"
            )
        elif error_num == -4:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid metadata key!")
        elif error_num == -5:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid metadata value!"
            )
        elif error_num == -6:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid coordinates!")
        elif error_num == -7:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid hub name")
        elif error_num == -8:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid zone name")
        elif error_num == -9:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid connection syntax"
            )

        elif error_num == -10:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid coordinates!")
        elif error_num == -11:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Invalid zone name!")

        elif error_num == -12:
            raise ValueError(
                f"\033[31m[Line {line_num + 1}]\033[0m Duplicate connection")


    def check_zone_duplicate(self, zone: Zone):
        for z in self.zones.values():
            if z.x == zone.x and z.y == zone.y:
                return -10
            elif z.name == zone.name:
                return -11
        return 0

    def parse(self):
        conns_names = []
        content_lines = self.get_file_content_lines
        for line_num, line in enumerate(content_lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            self.current_mode = self.mode_selecter(line)
            if self.current_mode == "EOF":
                self.finished_keys['connection'] = True
                break

            if self.current_mode == 'connection':
                self.finished_keys['hub'] = True
            if self.current_mode == -1 or self.check_order == -1:
                self.error_raiser(line_num, -1)
            elif ":" not in line:
                raise ValueError(
                    f"\033[31m[Line {line_num + 1}]\033[0m Invalid line: ':' is missing."
                )
            elif self.char_counter(line, ':') != 1:
                raise ValueError(
                    f"\033[31m[Line {line_num + 1}]\033[0m Invalid line: expected exactly one ':'."
                )

            if self.current_mode == "nb_drones":
                # return -1: duplicate nb_drones
                # return -2: invalid nb_drones syntax
                # return -3: invalid nb_drones value
                self.nb_drones = self.get_nb_drones(line)
                if self.nb_drones == -1:
                    raise ValueError(
                        f"\033[31m[Line {line_num + 1}]\033[0m Unexpected or duplicate key."
                    )
                elif self.nb_drones == -2:
                    raise ValueError(
                        f"\033[31m[Line {line_num + 1}]\033[0m Invalid nb_drones format!"
                    )
                elif self.nb_drones == -3:
                    raise ValueError(
                        f"\033[31m[Line {line_num + 1}]\033[0m Invalid nb_drones value!"
                    )
                self.finished_keys['nb_drones'] = True

            elif self.current_mode == "start_hub" or self.current_mode == "hub" or self.current_mode == "end_hub":
                zone = self.get_hub(line)

                if isinstance(zone, Zone) and zone.name:

                    if self.check_zone_duplicate(zone) == -10:
                        self.error_raiser(line_num, -10)
                    elif self.check_zone_duplicate(zone) == -11:
                        self.error_raiser(line_num, -11)
                    if self.current_mode == "start_hub":
                        self.finished_keys['start_hub'] = True
                        self.start_hub = zone
                    elif self.current_mode == "end_hub":
                        self.finished_keys['end_hub'] = True
                        self.end_hub = zone
                    self.zones[zone.name] = zone
                else:
                    self.error_raiser(line_num, zone)

            elif self.current_mode == 'connection':
                if self.char_counter(line, '-') != 1:
                    raise ValueError(
                        f"\033[31m[Line {line_num + 1}]\033[0m Invalid connection syntax"
                    )
                conn = self.get_connection(line)
                if isinstance(conn, Connection):
                    if conn.zone1.name == conn.zone2.name:
                        self.error_raiser(line_num, -11)
                    elif tuple(sorted([conn.zone1.name,
                                       conn.zone2.name])) not in conns_names:
                        self.connections.append(conn)
                        conns_names.append(
                            tuple(sorted([conn.zone1.name, conn.zone2.name])))
                    else:
                        self.error_raiser(line_num, -12)
                else:
                    self.error_raiser(line_num, conn)

        for key, val in self.finished_keys.items():
            if key != 'hub' and key != 'connection' and not val:
                raise ValueError(
                    f"\033[31m[ERROR]\033[0m Missing required key!")