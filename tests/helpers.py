import requests


def create_response(json_body={}, status_code=200, content=None):
    response = requests.Response()
    response.status_code = status_code
    response.json = lambda: json_body
    response._content = content
    return response
