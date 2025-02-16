# Particle Simulation

## Overview
This project is a particle simulation that models interactions between different classes of particles. The simulation allows users to configure the number of particles, their colors, mass, and their interaction strengths. The visualization is handled using VisPy, while the user interface is built with PySide6.

## Features
- Interactive GUI to configure particle properties
- Customizable particle interactions (attractive/repulsive forces)
- Real-time visualization using VisPy
- Adjustable simulation parameters (time step, particle size, etc.)
- Collision handling and response based on particle mass and restitution

## Installation
### Prerequisites
Make sure you have Python installed (>=3.8) and install the required dependencies:

```sh
pip install -r requirements.txt
```

## Usage
1. Run the main GUI script:
   ```sh
   python GUI.py
   ```
2. Configure the particle classes using the GUI:
   - Adjust the number of particles per color
   - Pick colors for different particle type
   - Pick mass and restitution
   - Modify interaction strengths between particle types
   - Save and start the simulation

## Project Structure
```sh
.
├── .github/workflows/      # CI/CD pipeline configuration
│   └── workflow.yaml
├── docs/                   # Documentation using Sphinx
│   ├── conf.py             # Sphinx configuration file
│   └── index.rst           # Documentation index
├── src/                    # Source code directory
│   ├── custom_widgets/     # Additional GUI widgets (e.g., color picker)
│   ├── GUI.py              # Main GUI application
│   ├── ParticleSystem.py   # Particle physics and simulation logic
│   ├── VisPyStack.py       # Visualization and rendering using VisPy
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_collision.py   # Test for collision detection
├── .gitignore              # Git ignore file
├── LICENSE                 # License file
├── README.md               # Project documentation
├── requirements.txt        # Dependency list for installation
```

## How It Works
### 1. GUI (`GUI.py`)
- The GUI is built in PySide and allows users to set up their simulation parameters.
- Controls include sliders, color pickers, and a relationship matrix to define interactions between particle types.

### 2. Simulation Engine (`ParticleSystem.py`)
- Implements the particle motion, interactions, and collisions.
- Uses a k-d tree for efficient neighbor searches.
- Supports Brownian motion and drag forces for realism.

    #### 2.1 Collision Handling:
    -  When two particles collide, their velocities are updated using an impulse-based method based on this fromula:

    $$ j = \frac{- (1 + e) ( \mathbf{v}_1^{AB} \cdot \mathbf{n} )}{ \mathbf{n} \cdot \mathbf{n} \left( \frac{1}{M^A} + \frac{1}{M^B} \right) } $$
    - Explenations:
        - $j$ is the impulse magnitude.
        - $e$ is the coefficient of restitution.
        - $\mathbf{v}_1^{AB}$ is the relative velocity before collision.
        - $\mathbf{n}$ is the normal vector at the collision point.
        - $M^A$ and $M^B$ are the masses of the two colliding particles.

    - The impulse is a force applied over a very short period that changes the velocities of both particles.

    - The magnitude of the impulse depends on the masses of the colliding particles and the coefficient of restitution.

    - The impulse is applied along the normal vector at the collision point.

    - The updated velocities account for the mass of each particle, meaning heavier particles experience less velocity change than lighter particles.








### 3. Visualization (`VisPyStack.py`)
- Uses VisPy to render the particle system efficiently.
- Updates particle positions dynamically based on physics calculations.


## License
This project is licensed under the MIT License.
