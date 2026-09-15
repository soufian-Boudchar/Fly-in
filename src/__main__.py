from .parsing.parser import ConfigParser
from .graph import Graph
import sys
from .classes import Connection, ZoneCost, Zone
from .path_finder import PathFinder
from .simulation import Simulation
from .visualizer import Visualizer



def main()-> None:
    config = ConfigParser(sys.argv)

    try:
        config.parse()
    except ValueError as e:
        print(e)
        exit(1)
        
    graph = Graph(config)
    graph.build_graph()
    
    path_finder = PathFinder(graph)
    path = path_finder.find_shortest_path()
    simulation = Simulation(graph, config.nb_drones, path)
    simulation.run()
    visualizer = Visualizer(simulation)
    visualizer.run_interactive()
if __name__ == "__main__":
    main()