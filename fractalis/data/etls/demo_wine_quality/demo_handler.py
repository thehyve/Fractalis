from fractalis.data.etlhandler import ETLHandler
from fractalis.data_services_config import Handler


class DemoHandler(ETLHandler):

    _handler = Handler.DEMO_WINE_QUALITY

    @staticmethod
    def make_label(descriptor):
        return descriptor.get('field')

    def _get_token_for_credentials(self, server: str, auth: dict) -> str:
        return 'foo'

    def _heartbeat(self):
        pass
