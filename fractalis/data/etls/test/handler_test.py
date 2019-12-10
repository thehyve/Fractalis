from fractalis.data.etlhandler import ETLHandler
from fractalis.data_services_config import Handler


class TestHandler(ETLHandler):

    _handler = Handler.TEST

    @staticmethod
    def make_label(descriptor):
        return descriptor.get('label')

    def _get_token_for_credentials(self, server: str, auth: dict) -> str:
        return 'abc'
