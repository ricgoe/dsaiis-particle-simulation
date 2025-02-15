class BackEnd():
    def __init__(self, Backend: bool=True):
        self.partycles = [1,2,3]
        self.time = 0
        self.Backend = Backend
    
    def party(self):
        """This function is a party
        
        Returns:
            int: 10 times the number of particles
        """
        return self.partycles * 10 