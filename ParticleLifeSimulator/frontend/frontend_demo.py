class FrontEnd():
    """End of the front"""
    def __init__(self, backend, amount):
        """This is the front end of the program

        Args:
            backend (bool): This is the backend of the program
            amount (int): This is the amount of particles
        """
        self.backend = backend
        self.time = 0
        self.particles = amount
    
    def party(self):
        """This function is a party
        
        Returns:
            int: 10 times the number of particles
        """
        return self.particles * 10