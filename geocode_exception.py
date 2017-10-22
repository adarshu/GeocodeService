# Copyright Adarsh Uppula, 2017
#

class MyException(Exception):
    """Raise for my specific kind of exception"""

    def __init__(self, message):
        self.message = message

    def __init__(self, type, message):
        self.type = type
        self.message = message
