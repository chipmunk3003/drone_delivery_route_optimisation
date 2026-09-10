# Drone Delivery Route Optimisation

A Python-based drone delivery simulation that combines graph algorithms, route optimisation, inventory management and an interactive map-based GUI.

The system simulates a delivery drone operating between warehouses and multiple customer locations while considering delivery order, payload capacity, battery consumption and charging requirements.

## Features

* Interactive map-based drone simulation
* Customer order placement
* SQLite-based order and inventory management
* Two-warehouse inventory system
* Drone payload and battery simulation
* Automatic delivery batching based on drone capacity
* Route optimisation using graph algorithms
* Warehouse selection based on inventory availability
* Charging-point integration
* Estimated delivery times
* Pause/resume simulation
* Manual or automatic delivery-tour initiation

## Technical Highlights

### Route optimisation

The project implements a graph-based approach to the travelling salesperson problem.

The optimisation pipeline uses:

1. Complete weighted graph construction
2. Kruskal's minimum spanning tree algorithm
3. Minimum-weight perfect matching of odd-degree vertices
4. Eulerian cycle construction
5. Eulerian shortcutting
6. Additional route improvement

The implementation was developed from the underlying algorithms rather than relying entirely on a pre-built TSP library.

### Drone simulation

The drone simulation models:

* geographic position
* payload
* battery level
* flight time
* charging time
* delivery progress

Distances between geographic coordinates are calculated using the Haversine formula.

### Inventory management

Orders are stored using SQLite and interact with stock held across two warehouses.

The system determines which warehouse or combination of warehouses must be visited to fulfil a delivery batch.

## Project Structure

```text
drone-delivery-optimisation/
│
├── src/
│   ├── algorithms/
│   │   ├── graph.py
│   │   └── route_optimizer.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── orders.py
│   │   └── inventory.py
│   │
│   ├── simulation/
│   │   ├── drone.py
│   │   ├── battery.py
│   │   └── geometry.py
│   │
│   └── ui/
│       ├── main_window.py
│       ├── order_frame.py
│       ├── map_frame.py
│       └── widgets.py
│
├── data/
├── assets/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies

* Python
* SQLite
* Tkinter
* tkintermapview
* Pillow
* Graph algorithms
* Haversine distance calculations
* Multithreading

## Installation

Clone the repository and install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Run:

```bash
python src/main.py
```

The application opens an interactive map where delivery locations can be selected and orders can be placed.

## How It Works

A simplified delivery cycle is:

```text
Customer orders
      ↓
Order added to queue
      ↓
Orders grouped into delivery batch
      ↓
Warehouse availability checked
      ↓
Candidate delivery route generated
      ↓
Battery requirements evaluated
      ↓
Charging stop added if necessary
      ↓
Optimised route displayed
      ↓
Drone simulation begins
      ↓
Orders delivered
      ↓
Inventory updated
```

## Algorithms

The project demonstrates practical applications of:

* Minimum spanning trees
* Kruskal's algorithm
* Minimum-weight matching
* Eulerian cycles
* Travelling salesperson problem approximations
* Greedy/first-fit bin packing
* Haversine distance
* Geographic bearing calculations

## Limitations

This is a simulation rather than a production drone-control system.

The route optimisation is an approximation-based approach rather than an exact solution to the travelling salesperson problem.

The simulation also uses simplified assumptions for drone speed, battery consumption and charging.

## Future Improvements

Possible future improvements include:

* Automated unit and integration testing
* Improved TSP optimisation
* More sophisticated battery modelling
* More realistic drone movement
* Better warehouse allocation
* Route-performance benchmarking
* Configuration files for simulation parameters
* Improved separation between GUI and application logic
* Packaging the application for easier installation

## Author

**Rujuta Joglekar**

Project demonstrating software engineering, algorithms, simulation and database development
