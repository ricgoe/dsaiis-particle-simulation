import numpy as np
import pytest
from src.particle_system import ParticleSystem

def test_collision_detection():
    ps = ParticleSystem(
        width=10,
        height=10,
        color_distribution=[((0, 0, 0), 4, 1, 1)],
        radius=1,
        interaction_matrix={(1, 1): 1}
    )
    
    # check for distances of lower than 2*radius
    # - Particle 0 at (0.0, 0.0)
    # - Particle 1 at (1.0, 1.0)  -- distance ~1.41 from Particle 0  -> collision with 0
    # - Particle 2 at (5.0, 5.0)  -- far away, no collisions
    # - Particle 3 at (0.0, 2.0)  -- distance 2.0 from Particle 0 and ~1.41 from Particle 1 -> collision
    # - Particle 4 at (9.9, 9.9)  -- Wrap-Around_Particle - distance ~0.14 from Particle 0 and ~1.56 from Particle 1 -> collision

    particles = np.array([
        [0.0, 0.0],
        [1.0, 1.0],
        [5.0, 5.0],
        [0.0, 2.0],
        [9.9, 9.9]
    ])
    
    i_idx, j_idx, distances, normals = ps.check_collisions(particles, ps.radius)
    
    # expected collisions (0,1), (0,4), (0,3), (1,4), (1,3)
    expected_collisions = (np.array([0, 0, 0, 1, 1]), np.array([1, 4, 3, 4, 3]))

    # assert that detected collisions match expected collisions
    assert np.array_equal(i_idx, expected_collisions[0])
    assert np.array_equal(j_idx, expected_collisions[1])
