class IOContextError(Exception):
    def __init__(self, message: str = "Error while handling the IO Context"):
        self.message = message
        super().__init__(self.message)


class DataIOError(Exception):
    def __init__(self, message: str = "Error while performing IO operations"):
        self.message = message
        super().__init__(self.message)
