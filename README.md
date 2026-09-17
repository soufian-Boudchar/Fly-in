*This project has been created as part of the 42 curriculum by sboudcha.*

# Fly-in

An efficient multi-drone movement simulation engine and interactive visualizer. **Fly-in** routes a fleet of drones from a central base (start) to a target location (end) through a dynamic network, minimizing the total number of simulation turns while strictly adhering to physical and movement constraints.

---

## 📖 Description

The core objective of this project is to navigate autonomous drones across a graph represented as a network of connected zones. Drones may move simultaneously, but the simulation must respect strict rules to avoid collisions and deadlocks. 

The system handles different zone types with specific movement costs:
* **normal:** Standard zone costing 1 turn.
* **restricted:** A sensitive zone requiring 2 turns to traverse.
* **priority:** Preferred pathfinding zone costing 1 turn.
* **blocked:** Inaccessible zones that drones cannot enter or pass through.

Additionally, the engine strictly enforces `max_drones` (zone occupancy capacity) and `max_link_capacity` (connection bandwidth) during every turn.

---

## 🧮 Algorithm Choices & Implementation Strategy

To ensure drones are distributed efficiently without dynamic collisions or bottleneck congestion, the engine employs a Multi-Agent Pathfinding (MAPF) strategy:

1. **Object-Oriented Graph Representation:**
   The network is fully object-oriented and does not rely on forbidden external libraries like `networkx`. Nodes and edges encapsulate their own capacity and state logic.

2. **Flow & Path Allocation:**
   The algorithm calculates disjoint and overlapping paths, accounting for the movement costs associated with zone types (e.g., favoring `priority` zones and calculating multi-turn offsets for `restricted` zones).

3. **Turn-Based Scheduling:**
   At each discrete turn, the scheduler evaluates the graph state. It verifies that moving a drone will not exceed the destination's `max_drones` or the connection's `max_link_capacity` before executing the move. If a drone moves to a restricted zone, it occupies the connection during transit and arrives strictly on the second turn without waiting extra turns on the connection.

---

## 🎨 Visual Representation & User Experience

To enhance the understanding of the simulation and quickly identify bottlenecks, **Fly-in** features a Pygame-based graphical interface (alongside colored terminal output). 

**Key UX Enhancements:**
* **Real-time Map Scaling:** Automatically centers the graph to fit the user's screen.
* **Live Capacity Indicators:** Colors and badges dynamically update to show zone occupancy and connection saturation.
* **Turn-by-Turn Interactivity:** Allows the user to step through the simulation visually, making it significantly easier to debug paths and verify simultaneous drone movements compared to reading raw text logs.

---

## 🛠️ Instructions

### Prerequisites
* Python 3.10 or later.
* `pygame` for the visualizer.
* `flake8` and `mypy` for mandatory static type checking and linting.

### Compilation & Execution
The project uses a `Makefile` to automate common tasks.

1. **Install dependencies:**
   make install

```

2. **Run the simulation:**
```bash
make run
# OR directly via python
python3 main.py maps/subject_map.txt

```


3. **Run code linters (flake8 & mypy):**
```bash
make lint

```


4. **Clean cache files:**
```bash
make clean

```



---

## 📝 Example Input & Expected Output

### Input Map File format

```text
nb_drones: 2
start_hub: start 0 0
end_hub: goal 10 10
hub: roof1 3 4
hub: corridorA 4 3 [zone=priority max_drones=2]
connection: start-roof1
connection: start-corridorA
connection: roof1-goal
connection: corridorA-goal

```

### Expected Output

The standard output strictly follows the simulation turn format:

```text
D1-roof1 D2-corridorA
D1-goal D2-goal

```

---

## 📚 Resources

### References

* **Multi-Agent Pathfinding (MAPF):** Concepts of collision-free agent routing.
* **Network Flow Algorithms:** Handling dynamic capacities on edges/nodes.
* **Pygame Documentation:** For rendering the visual representation.

### AI Usage Disclosure

As encouraged by the curriculum for learning purposes, AI tools (LLMs) were utilized as engineering assistants during development to:

1. **Optimize Pygame Rendering:** Assisting with coordinate bounds calculation to auto-scale the graphical visual interface.
2. **Type Safety Troubleshooting:** Resolving complex type assignment errors with `mypy` (e.g., Pygame surface typing) to ensure 100% strict type safety.


3. **Parsing Logic Guidance:** Discussing and structuring the initial regex/parsing logic to cleanly handle optional metadata tags like `[color=red max_drones=2]`. All generated ideas were thoroughly peer-reviewed and manually implemented.
