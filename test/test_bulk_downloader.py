import unittest
from mock import patch, MagicMock

from download_espa_order import Api, Scene, LocalStorage, main
from mocks.espa_api import MockApiRequest, MockDownloadRequest


class TestAPIInteraction(unittest.TestCase):
    def setUp(self):
        self.host = 'invalidhost.com'
        self.username = 'production'
        self.password = 'secret1'
        self.api = Api(self.host, self.username, self.password)
        self.email = 'production@email.com'
        self.orderid = 'production@email.com-0000-00-00'
        self.target_directory = '/invalid/path'

    def tearDown(self):
        pass

    @patch('download_espa_order.Api.api_request', MockApiRequest)
    def test_api_get_completed_scenes(self):
        orders = self.api.retrieve_all_orders(self.email)
        self.assertIsInstance(orders, list)
        self.assertIn(self.orderid, orders)

    @patch('download_espa_order.Api.api_request', MockApiRequest)
    def test_get_items(self):
        scenes = self.api.get_completed_scenes(self.orderid)
        self.assertIsInstance(scenes, list)

    @patch('download_espa_order.ul.urlopen', MockDownloadRequest)
    @patch('download_espa_order.Api.api_request', MockApiRequest)
    @patch('download_espa_order.os.mkdir', lambda x, y: True)
    @patch('download_espa_order.os.rename', lambda x, y: True)
    def test_main(self):
        main(self.username, self.email, self.orderid, self.target_directory,
             password=self.password)


class TestUserErrors(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass



class TestAPIErrors(unittest.TestCase):
    pass
