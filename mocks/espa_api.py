class MockApiRequest(dict):
    def __init__(self, *args, **kwargs):
        super(MockApiRequest, self).__init__()
        url = args[0]

        self.store = dict()
        if 'item-status' in url:
            self.update({'orderid': {'production@email.com-0000-00-00': [{
                "product_dload_url": "http://download.com/filename.tar.gz"
            }]}})
        if 'list-orders' in url:
            self.update({'orders': ['production@email.com-0000-00-00']})
        if 'order-status' in url:
            self.update({'orderid': 'production@email.com-0000-00-00', 'status': 'complete'})
