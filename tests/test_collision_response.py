from ParticleSystem import ParticleSystem
import numpy as np

def test_update_velocities_collisions_single():
    """
      - Particle 0 at [1.0, 1.0]
      - Particle 1 at [1.5, 1.0]
      
    With radius = 1, the overlap depth is:
      depth = 2 * radius - distance = 2 - 0.5 = 1.5
      
    Collision normal (computed as (p0 - p1)/distance) is:
      normal = [-0.5, 0] / 0.5 = [-1, 0]
      
    Positions are updated as:
      p0_new = p0 + 0.5 * depth * normal = [1, 1] + 0.75 * [-1, 0] = [0.25, 1]
      p1_new = p1 - 0.5 * depth * normal = [1.5, 1] - (-0.75, 0) = [2.25, 1]
      
    For velocities, assuming:
      v0 = [1, 0], v1 = [-1, 0]
      Relative velocity: v_rel = v1 - v0 = [-2, 0]
      dot = (-2)*(-1) + 0 = 2
      Factor = -(1 + e)*dot, with e = 0.5, so factor = -1.5*2 = -3.
      Denom = (1/m0 + 1/m1) = 2, impulse = -3/2 = -1.5.
      
      Then:
        v0_new = v0 - (impulse/m0)*normal = [1, 0] - (-1.5)*[-1, 0] = [1, 0] - [1.5, 0] = [-0.5, 0]
        v1_new = v1 + (impulse/m1)*normal = [-1, 0] + (-1.5)*[-1, 0] = [-1, 0] + [1.5, 0] = [0.5, 0]
    """

    ps = ParticleSystem(
        width=10,
        height=10,
        color_distribution=[((1, 0, 0, 1), 2, 0.5, 1)],
        radius=1,
        interaction_matrix={(1, 1): 1}
    )
    
    # set state variables to match scenario
    ps._particles = np.array([[1.0, 1.0], [1.5, 1.0]], dtype=float)
    ps._velocity = np.array([[1.0, 0.0], [-1.0, 0.0]], dtype=float)
    ps._restitution = np.array([0.5, 0.5], dtype=float)
    ps._mass = np.array([1.0, 1.0], dtype=float)
    
    # Compute collision data as if returned by check_collisions.
    diff = ps.positions[0] - ps.positions[1]
    distance = np.linalg.norm(diff)
    normal = diff / distance if distance != 0 else np.array([0.0, 0.0])
    colliding_data = (
        np.array([0]),                # i_idx
        np.array([1]),                # j_idx
        np.array([distance]),         # distances
        np.array([normal])            # normals
    )
    
    pos = ps.positions.copy()
    # update velocities and positions
    ps.update_velocities_collisions(pos, colliding_data, mode="collision")
    # Expected updated positions.
    depth = 2 * ps.radius - distance  # 2 - 0.5 = 1.5
    expected_p0 = pos[0] + 0.5 * depth * normal  # [1,1] + 0.75*[-1,0] = [0.25, 1]
    expected_p1 = pos[1] - 0.5 * depth * normal  # [1.5,1] - (-0.75,0) = [2.25, 1]
    
    np.testing.assert_allclose(ps.positions[0], expected_p0, atol=1e-6,
                               err_msg=f"Particle 0 position not updated correctly, expected {expected_p0} but got {ps.positions[0]}")
    np.testing.assert_allclose(ps.positions[1], expected_p1, atol=1e-6,
                               err_msg=f"Particle 1 position not updated correctly, expected {expected_p1} but got {ps.positions[1]}")
    
    # expected velocities
    expected_v0 = np.array([-0.5, 0.0])
    expected_v1 = np.array([0.5, 0.0])
    
    np.testing.assert_allclose(ps._velocity[0], expected_v0, atol=1e-6,
                               err_msg="Particle 0 velocity not updated correctly.")
    np.testing.assert_allclose(ps._velocity[1], expected_v1, atol=1e-6,
                               err_msg="Particle 1 velocity not updated correctly.")
