class ServiceUnavailableException(Exception):
    def __init__(self, message="Service is temporarily unavailable."):
        self.message = message
        super().__init__(self.message)

class TranslationServiceUnavailable(ServiceUnavailableException):
    def __init__(self, message="Translation service is temporarily unavailable."):
        super().__init__(message)
