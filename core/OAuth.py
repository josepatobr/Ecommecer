from google_auth_oauthlib.flow import InstalledAppFlow
import requests
from google.auth.transport.requests import Request

scope = 'https://www.googleapis.com/auth/userinfo.profile'
flow = InstalledAppFlow.from_client_secrets_file(
    'core/client_id.json', [scope])

credentials = flow.run_local_server(port=8080)


response = requests.get(
    'https://www.googleapis.com/userinfo/v2/me',
    headers={'Authorization': f'Bearer {credentials.token}'}
)

if credentials.expired and credentials.refresh_token:
    credentials.refresh(Request())
