from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
import os
import pickle

scope = 'https://www.googleapis.com/auth/userinfo.profile'
token_path = 'core/token.pickle'

credentials = None

if os.path.exists(token_path):
    with open(token_path, 'rb') as token_file:
        credentials = pickle.load(token_file)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'core/client_id.json', [scope]
        )
        credentials = flow.run_local_server(port=8080)

    with open(token_path, 'wb') as token_file:
        pickle.dump(credentials, token_file)

response = requests.get(
    'https://www.googleapis.com/userinfo/v2/me',
    headers={'Authorization': f'Bearer {credentials.token}'}
)

print(response.json())