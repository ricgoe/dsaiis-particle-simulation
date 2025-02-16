import numpy as np
import pytest
from ParticleSystem import ParticleSystem
import copy

color_distribution = {
    "key1": { "color": (1.0, 0.0, 0.0, 1.0), "n": 375, "mass": 1, "bounciness": 1.0,}
}

relationships = {
    (1, 1): {"value": 0},
    (1, 2): {"value": 0},
    (2, 1): {"value": 0},
    (2, 2): {"value": 0},
}

def test_particle_position_init():
    ps = ParticleSystem(
        width=10,
        height=10,
        color_distribution=color_distribution,
        radius=1,
        interaction_matrix=relationships
    )
    
    np.testing.assert_array_less(ps.positions[:, 0] - 0, np.full(ps.positions.shape[0], ps._width + 1), 
                               err_msg="x-positions exceed canvas width.")
    
    
def test_invalid_mass():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution["key1"]["mass"] = -1
    with pytest.raises(ValueError, match="Mass must be greater than 0"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # mass = -1
            radius=1,
            interaction_matrix=relationships
        )


def test_invalid_restitution_negative():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution['key1']['bounciness'] = -1
    print(_color_distribution)
    with pytest.raises(ValueError, match="Restitution coefficient must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # restitution < 0
            radius=1,
            interaction_matrix=relationships
        )


def test_invalid_restitution_over():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution['key1']['bounciness'] = 1.5
    with pytest.raises(ValueError, match="Restitution coefficient must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # restitution > 1 (gaining energy)
            radius=1,
            interaction_matrix=relationships
        )


def test_invalid_rgba_length():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution['key1']['color'] = (0,0,0)
    with pytest.raises(ValueError, match="RGBA color must have 4 elements"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # only rgb values instead of rgba
            radius=1,
            interaction_matrix=relationships
        )


def test_invalid_rgba_values_negative():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution['key1']['color'] = (-1,0,0,1)
    with pytest.raises(ValueError, match="RGBA color values must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # -1 is invalid
            radius=1,
            interaction_matrix=relationships
        )


def test_invalid_rgba_values_above_one():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution['key1']['color'] = (255,1,1,1)
    with pytest.raises(ValueError, match="RGBA color values must be between 0 and 1"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # 255 is invalid
            radius=1,
            interaction_matrix=relationships
        )


def test_invalid_particle_number_negative():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution['key1']['n'] = -5
    with pytest.raises(ValueError, match="Number of particles must be a non-negative integer"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # negative number
            radius=1,
            interaction_matrix=relationships
        )


def test_invalid_particle_number_non_integer():
    _color_distribution = copy.deepcopy(color_distribution)
    _color_distribution['key1']['n'] = 5.5
    with pytest.raises(ValueError, match="Number of particles must be a non-negative integer"):
        ParticleSystem(
            width=100,
            height=100,
            color_distribution=_color_distribution,  # 5.5 is not an integer
            radius=1,
            interaction_matrix=relationships
        )
        
def test_particle_initialization_color_indices_colors_masses():
    width, height = 100, 100
    
    color_distribution = {
        "key1": {
            "color": (1, 0, 0, 1),
            "n": 3,
            "mass": 2,
            "bounciness": 1,
        },
        "key2": {
            "color": (0, 1, 0, 1),
            "n": 2,
            "mass": 3,
            "bounciness": 1,
        },
    }

    ps = ParticleSystem(
        width=width,
        height=height,
        color_distribution=color_distribution,
        interaction_matrix=relationships,
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