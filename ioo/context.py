import abc


class AbstractContextProvider(abc.ABC):
    @abc.abstractmethod
    def get_context_provider_data(self, request, **kwargs):
        return {**kwargs}


class BaseContextProvider(AbstractContextProvider):
    def __init__(self):
        self.session_id = 0

    def get_context_provider_data(self, request, **kwargs):
        self.session_id = request.user.session_id
        return {}
