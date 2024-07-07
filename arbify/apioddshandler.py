import requests

class ApiOddsHandler:
     def __init__(self, api_key):
         self.api_key = api_key
         self.host = 'https://api.the-odds-api.com'

    def get_sports(self):
        url = f'{self.host}/v4/sports/?apiKey={self.api_key}'
        print(f'Making request to endpoint {url}')
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print(f'Something went wrong making request to {url}')
            return
        return response.json()
