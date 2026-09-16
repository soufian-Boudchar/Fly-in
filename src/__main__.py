from src.parsing.parser import ConfigParser
from src.graph import Graph
import sys
from src.path_finder import PathFinder
from src.simulation import Simulation


def main() -> None:
    config = ConfigParser(sys.argv)

    try:
        config.parse()
        graph = Graph(config)
        graph.build_graph()
        path_finder = PathFinder(graph)

        paths = path_finder.get_path()
        simulation = Simulation(graph, config.nb_drones, paths)
        simulation.run()

    except ValueError as e:
        print(e)
        exit(1)
    except FileNotFoundError:
        print(f"\033[31m[ERROR]\033[0m No such file: '{sys.argv[1]}'!")
        exit(1)
    except PermissionError:
        print(f"\033[31m[ERROR]\033[0m Permission denied: '{sys.argv[1]}'")
        exit(1)
    except IsADirectoryError as e:
        print(e)
        exit(1)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
