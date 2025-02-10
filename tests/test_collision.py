import numpy as np
import pytest
from src.particle_system import ParticleSystem

def test_collision_detection():
    ps = ParticleSystem(
        width=10,
        height=10,
        color_distribution=[((0, 0, 0), 4)],
        radius=1
    )
    
    # - Particle 1 at (0.0, 0.0)
    # - Particle 2 at (1.0, 1.0)  -- distance ~1.41 from Particle 0  -> collision with 0
    # - Particle 3 at (5.0, 5.0)  -- far away, no collisions
    # - Particle 4 at (0.0, 2.0)  -- distance 2.0 from Particle 0 and ~1.41 from Particle 1 -> collision
    #TODO add another particle which has overlapping bounding boxes but is not colliding
    particles = np.array([
        [0.0, 0.0, 0, 0, 0],
        [1.0, 1.0, 0, 0, 0],
        [5.0, 5.0, 0, 0, 0],
        [0.0, 2.0, 0, 0, 0]
    ])
    
    collisions = ps.check_collisions(particles)
    
    # order of indices in each pair is not important
    expected_collisions = {frozenset({0, 1}), frozenset({0, 3}), frozenset({1, 3})}
    
    # convert list of collision pairs into set of frozensets for order-independent comparison
    actual_collisions = {frozenset(pair) for pair in collisions}
    
    # assert that detected collisions match expected collisions
    assert actual_collisions == expected_collisions
