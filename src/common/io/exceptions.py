from src.common.io import context


class IOContextError(Exception):
    def __init__(self, message: str, io_context: context.IOContext):
        self.io_context = io_context
        super().__init__(message)


class IOBuilderError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
