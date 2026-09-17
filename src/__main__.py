from src.parsing.parser import ConfigParser
from src.graph import Graph
import sys
from src.path_finder import PathFinder
from src.simulation import Simulation
from src.visualizer import Visualizer


def main() -> None:
    """Main execution entry point for parsing,
    pathfinding, and interactive simulation.

    Parses command-line arguments to build graph network,
    computes optimal routes,
    and runs simulation visualizer
    while handling execution errors gracefully.

    Raises:
        ValueError: On parsing syntax or semantic graph errors.
        FileNotFoundError: When configuration file path is invalid.
        PermissionError: When file access permission is denied.
        IsADirectoryError: When input path targets a directory.
    """
    config = ConfigParser(sys.argv)

    try:
        config.parse()
        graph = Graph(config)
        graph.build_graph()
        path_finder = PathFinder(graph)

        paths = path_finder.get_path()
        simulation = Simulation(graph, config.nb_drones, paths)
        vis = Visualizer(simulation)
        vis.run_interactive()
    except ValueError as e:
        print(e)
        exit(1)
    except FileNotFoundError:
        print(f"\033[31m[ERROR]\033[0m No such file: '{sys.argv[1]}'!")
        exit(1)
    except PermissionError:
        print(f"\033[31m[ERROR]\033[0m Permission denied: '{sys.argv[1]}'")
        exit(1)
    except IsADirectoryError:
        print(f"\033[31m[ERROR]\033[0m Is a directory '{sys.argv[1]}'")
        exit(1)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
