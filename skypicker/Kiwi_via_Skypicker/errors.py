class KiwiAPIError(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return '\n'.join(self.response.json()['errors'])
