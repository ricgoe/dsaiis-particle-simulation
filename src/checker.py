class Checker():
    def __init__(self, arg_1, arg_2):
        """Class to check implementation of the Sphinx - Documentation"""
        self.arg_1 = arg_1
        self.arg_2 = arg_2
    
    def check(self, arg_3):
        """A mehod be shown in the docs
        Args:
            arg_3 (int): A number to be checked

        Returns:
            bool: True if arg_3 is equal to arg_1, False otherwise
        """
        return arg_3 == self.arg_1
    
    
