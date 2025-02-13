# Particle Life Simulation

An interactive simulation based on particle life models.
It visualizes how particles organize themselves and form patterns through forces of attraction and repulsion.

![Particle Life Demo](docs/Demo) /////////

## Features
- **Visual animation**: Real-time visualization of particles
- **Customizable parameters**: Configurable attraction and repulsion forces
- **Efficient implementation**: Optimized for large particle volumes

## Installation & Setup

### Installation
```sh
git clone https://github.com/ricgoe/dsaiis-particle-simulation.git
cd dsaiis-particle-simulation
pip install -r requirements.txt
```

### Start the simulation
```sh
python GUI.py
```

This automatically starts the user interface. Here you can add particle types and manipulate parameters such as attraction and repulsion forces. To keep the particles apart, the individual particle types can each be given their own color. 
The quantity can be determined individually for each particle type.
Furthermore, the forces of attraction and repulsion can be set individually for each relation. 

As soon as the desired parameters have been set, the simulation can be started by clicking the ‘Save’ button.
To return to the standard parameters, you can use the ‘Reset’ button.

## Background & Algorithm
The project is based on particle-based simulations. The particles interact based on simple rules:

1. **Attraction**: Certain particles attract each other
2. **Repulsion**: Other particles repel each other

This creates a dynamic with which the particles adapt based on the forces.