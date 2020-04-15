import abc


def get_context_provider(request, page):
    template_name = page.get_template(request)
    for item in AbstractPageContextProvider.__subclasses__():
        if item.template_name == template_name:
            return item


class AbstractPageContextProvider(abc.ABC):

    @property
    @abc.abstractmethod
    def template_name():
        return ''

    @staticmethod
    @abc.abstractmethod
    def get_context_data(request, page):
        return {}
