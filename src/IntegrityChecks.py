import numpy as np

def _validate_particle_entry(rgba, num, restitution, mass):
        """
        Validates particle entry parameters.
        
        Parameters
        ----------
        rgba : tuple[int, int, int, int]
            A tuple containing the RGBA color of the particle.
        num : int
            The number of particles.
        restitution : float
            The restitution coefficient of the particle.
        mass : float
            The mass of the particle.
        
        Raises
        ------
        ValueError
            If any of the parameters are invalid.
        """
        if mass <= 0:
            raise ValueError("Mass must be greater than 0")
        if not (0 <= restitution <= 1):
            raise ValueError("Restitution coefficient must be between 0 and 1")
        if len(rgba) != 4:
            raise ValueError("RGBA color must have 4 elements")
        if not (np.all(np.array(rgba) >= 0) and np.all(np.array(rgba) <= 1)):
            raise ValueError("RGBA color values must be between 0 and 1")
        if not isinstance(num, int) or num < 0:
            raise ValueError("Number of particles must be a non-negative integer")