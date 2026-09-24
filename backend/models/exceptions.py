class ServiceUnavailableException(Exception):
    def __init__(self, message="Service is temporarily unavailable."):
        self.message = message
        super().__init__(self.message)
