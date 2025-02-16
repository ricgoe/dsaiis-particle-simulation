import numpy as np
import pytest
from ParticleSystem import ParticleSystem

# helper function
def dummy_interaction_matrix():
    return {(1, 1): 1.0}

def test_particle_position_init():
    ps = ParticleSystem(
        width=10,
        height=10,
        color_distribution=[((1, 0, 0, 1), 100, 1, 1)],
        radius=1,
        interaction_matrix={(1, 1): 1}
    )
    
    np.testing.assert_array_less(ps.positions[:, 0] - 0, np.full(ps.positions.shape[0], ps.width + 1), 
                               err_msg="x-positions exceed canvas width.")
    
    
def test_invalid_mass():
    with pytest.raises(ValueError, match="Mass must be greater than 0"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, 0, 1), 10, 0.5, 0)],  # mass = 0
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )


def test_invalid_restitution_negative():
    with pytest.raises(ValueError, match="Restitution coefficient must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, 0, 1), 10, -0.1, 1)],  # restitution < 0
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )


def test_invalid_restitution_over():
    with pytest.raises(ValueError, match="Restitution coefficient must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, 0, 1), 10, 1.1, 1)],  # restitution > 1 (gaining energy)
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )


def test_invalid_rgba_length():
    with pytest.raises(ValueError, match="RGBA color must have 4 elements"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, 0), 10, 0.5, 1)],  # only rgb values instead of rgba
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )


def test_invalid_rgba_values_negative():
    with pytest.raises(ValueError, match="RGBA color values must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, -0.1, 1), 10, 0.5, 1)],  # -0.1 is invalid
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )


def test_invalid_rgba_values_above_one():
    with pytest.raises(ValueError, match="RGBA color values must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, 1.2, 1), 10, 0.5, 1)],  # 1.2 is invalid
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )


def test_invalid_particle_number_negative():
    with pytest.raises(ValueError, match="Number of particles must be a non-negative integer"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, 0, 1), -5, 0.5, 1)],  # negative number
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )


def test_invalid_particle_number_non_integer():
    with pytest.raises(ValueError, match="Number of particles must be a non-negative integer"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=[((0, 0, 0, 1), 5.5, 0.5, 1)],  # 5.5 is not an integer
            radius=1,
            interaction_matrix=dummy_interaction_matrix()
        )
        
def test_particle_initialization_color_indices_colors_masses():
    width, height = 100, 100
    color_distribution = [
        ((1, 0, 0, 1), 3, 1, 2),   # class 1: red particles, count=3, mass=2
        ((0, 1, 0, 1), 2, 0.8, 3)  # class 2: green particles, count=2, mass=3
    ]

    interaction_matrix = {
        (1, 1): 1.0,
        (1, 2): 1.0,
        (2, 2): 1.0
    }

    ps = ParticleSystem(
        width=width,
        height=height,
        color_distribution=color_distribution,
        interaction_matrix=interaction_matrix,
        radius=1
    )

    # colors array
    expected_colors_class1 = np.tile(np.array([1, 0, 0, 1]), (3, 1))
    expected_colors_class2 = np.tile(np.array([0, 1, 0, 1]), (2, 1))
    expected_colors = np.concatenate([expected_colors_class1, expected_colors_class2], axis=0)

    # color_indices array
    expected_indices_class1 = np.full((3, 1), 1)
    expected_indices_class2 = np.full((2, 1), 2)
    expected_color_indices = np.concatenate([expected_indices_class1, expected_indices_class2], axis=0)

    # masses array
    expected_masses_class1 = np.full(3, 2)
    expected_masses_class2 = np.full(2, 3)
    expected_masses = np.concatenate([expected_masses_class1, expected_masses_class2])

    # compare outputs to the expected values
    np.testing.assert_array_equal(ps._colors, expected_colors,
        err_msg="The colors array does not match the expected output.")
    np.testing.assert_array_equal(ps._color_index, expected_color_indices,
        err_msg="The color indices array does not match the expected output.")
    np.testing.assert_array_equal(ps._mass, expected_masses,
        err_msg="The masses array does not match the expected output.")