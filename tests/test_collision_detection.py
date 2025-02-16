import numpy as np
import pytest
from ParticleSystem import ParticleSystem

# helper function that creates a ParticleSystem instance
def create_system(distribution, width=10, height=10, radius=1):
    return ParticleSystem(
        width=width,
        height=height,
        color_distribution=distribution,
        radius=radius,
        interaction_matrix={(1, 1): 1}
    )
color_distribution = {
    "key1": { "color": (1.0, 0.0, 0.0, 1.0), "n": 375, "mass": 1, "bounciness": 1.0,}
}

relationships = {
    (1, 1): {"value": 0},
    (1, 2): {"value": 0},
    (2, 1): {"value": 0},
    (2, 2): {"value": 0},
}

def test_no_collisions():
    """
    Test that when particles are far apart, no collisions should be detected.
    """
    ps = create_system(color_distribution)
    particles = np.array([
        [1.0, 1.0],
        [5.0, 5.0],
        [8.0, 8.0]
    ])
    arr = ps.check_collisions(particles, 2*ps._radius)
    
    #expect all outputs to be empty arrays
    assert arr.size == 0, "Expected no collision"
    
    
def test_single_collision_no_wrap():
    """
    Test imple collision between two particles (without wrap-around effects).
    """
    ps = create_system(color_distribution)
    # two close particles, one far away.
    particles = np.array([
        [1.0, 1.0],   # Particle 0
        [1.0, 1.5],   # Particle 1 (close to 0)
        [5.0, 5.0]    
    ])
    arr = ps.check_collisions(particles, 2*ps._radius)
    
    # expect collision (0,1)
    np.testing.assert_array_equal(arr[:,0].astype(int), np.array([0]), err_msg="i indices mismatch")
    np.testing.assert_array_equal(arr[:,1].astype(int), np.array([1]), err_msg="j indices mismatch")
    np.testing.assert_allclose(arr[:,2], np.array([0.5]), atol=1e-7, err_msg="Distance incorrect")
    np.testing.assert_allclose(arr[:,3:], np.array([[0.0, -1.0]]), atol=1e-7, err_msg="Normal incorrect")
    

def test_collision_wrap_around():
    """
    Test collision detection over periodic boundaries (wrap-around effect).
    """
    ps = create_system(color_distribution, width=10, height=10, radius=1)
    particles = np.array([
        [0.5, 5.0],   # Particle 0 near left edge
        [9.5, 5.0]    # Particle 1 near right edge
    ])
    arr = ps.check_collisions(particles, ps._radius)
    
    # expected: dx = (0.5 - 9.5 + 5) % 10 - 5 = 1, dy = 0.
    np.testing.assert_array_equal(arr[:,0].astype(int), np.array([0]), err_msg="Wrap-around: i indices mismatch")
    np.testing.assert_array_equal(arr[:,1].astype(int), np.array([1]), err_msg="Wrap-around: j indices mismatch")
    np.testing.assert_allclose(arr[:,2], np.array([1.0]), atol=1e-7, err_msg="Wrap-around: Distance incorrect")
    np.testing.assert_allclose(arr[:,3:], np.array([[1.0, 0.0]]), atol=1e-7, err_msg="Wrap-around: Normal incorrect")


def test_collision_zero_distance():
    """
    Test edge-case when two particles overlap exactly (zero distance), even if very unlikely.
    """
    ps = create_system(color_distribution)
    particles = np.array([
        [3.0, 3.0],   # Particle 0
        [3.0, 3.0],   # Particle 1 (overlaps with 0)
        [8.0, 8.0]
    ])
    arr = ps.check_collisions(particles, ps._radius)
    
    # distance is 0 between overlapping parts, computed normal should be [0, 0].
    np.testing.assert_array_equal(arr[:,0].astype(int), np.array([0]), err_msg="Zero-distance: i indices mismatch")
    np.testing.assert_array_equal(arr[:,1].astype(int), np.array([1]), err_msg="Zero-distance: j indices mismatch")
    np.testing.assert_allclose(arr[:,2], np.array([0.0]), atol=1e-7, err_msg="Zero-distance: Distance should be 0")
    np.testing.assert_allclose(arr[:,3:], np.array([[0.0, 0.0]]), atol=1e-7, err_msg="Zero-distance: Normal should be [0,0]")


def test_multiple_collisions():
    """Test multiple collisions among four particles arranged in a square."""
    ps = create_system(color_distribution)
    particles = np.array([
        [1.0, 1.0],
        [1.0, 1.4],
        [1.4, 1.0],
        [1.4, 1.4]  
    ])
    arr = ps.check_collisions(particles, ps._radius)
    
    # (0,1): difference = (0, -0.4)  -> distance 0.4, normal (0, -1)
    # (0,2): difference = (-0.4, 0)  -> distance 0.4, normal (-1, 0)
    # (0,3): difference = (-0.4, -0.4) -> distance ~0.565685, normal ~(-0.70710678, -0.70710678)
    # (1,2): difference = (-0.4, 0.4)  -> distance ~0.565685, normal ~(-0.70710678, 0.70710678)
    # (1,3): difference = (-0.4, 0)    -> distance 0.4, normal (-1, 0)
    # (2,3): difference = (0, -0.4)    -> distance 0.4, normal (0, -1)
    expected = {
        (0, 1): (0.4, np.array([0.0, -1.0])),
        (0, 2): (0.4, np.array([-1.0, 0.0])),
        (0, 3): (np.sqrt(0.4**2 + 0.4**2), np.array([-0.70710678, -0.70710678])),
        (1, 2): (np.sqrt(0.4**2 + 0.4**2), np.array([-0.70710678,  0.70710678])),
        (1, 3): (0.4, np.array([-1.0, 0.0])),
        (2, 3): (0.4, np.array([0.0, -1.0]))
    }
    
    # sort detected collisions by (i_idx, j_idx)
    collisions = sorted(zip(arr[:,0].astype(int), arr[:,1].astype(int), arr[:,2], arr[:,3:]), key=lambda x: (x[0], x[1]))
    # expected sorted list
    expected_sorted = sorted(expected.items(), key=lambda x: x[0])
    
    for ((i_exp, j_exp), (d_exp, n_exp)), (i_obs, j_obs, d_obs, n_obs) in zip(expected_sorted, collisions):
        assert i_exp == i_obs, f"Expected collision pair index i: {i_exp} but got {i_obs}"
        assert j_exp == j_obs, f"Expected collision pair index j: {j_exp} but got {j_obs}"
        np.testing.assert_allclose(d_obs, d_exp, atol=1e-6,
                                   err_msg=f"Distance mismatch for collision pair ({i_exp}, {j_exp})")
        np.testing.assert_allclose(n_obs, n_exp, atol=1e-6,
                                   err_msg=f"Normal mismatch for collision pair ({i_exp}, {j_exp})")
