from google_images_search import GoogleImagesSearch
import requests

GCS_DEVELOPER_KEY = "AIzaSyCWa2t69aH0svy2rqBndDtcjWxivrnx7Po"
GCS_CX = "https://cse.google.com/cse.js?cx=d433024d3a51f4e8c"

gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

search_params = {
            'q': 'ВАШЕ_СЛОВО',
            'num': 1}
gis.search(search_params)

response = requests.get((gis.results())[0])


359090283474-i9l01iaj8rec56r9a4nd5hi7e67dvb33.apps.googleusercontent.com

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Путь к вашему файлу учетных данных JSON
credentials_path = 'путь_к_вашему_файлу_учетных_данных.json'

# Список разрешенных типов файлов
mime_types = ['image/jpeg', 'image/png']

# Ваш поисковый запрос
search_word = 'ваше_слово'


def authenticate(credentials_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=[
        'https://www.googleapis.com/auth/photoslibrary.readonly'])

    if credentials.expired:
        credentials.refresh(Request())

    return credentials


def search_photos(credentials, search_word):
    service = build('photoslibrary', 'v1', credentials=credentials)
    results = service.mediaItems().search(body={'pageToken': '', 'pageSize': 100,
                                                'filters': {'contentFilter': {'includedContentCategories': mime_types},
                                                            'featureFilter': {
                                                                'includedFeatures': search_word}}}).execute()

    photos = results.get('mediaItems', [])
    if not photos:
        return None

    return photos[0].get('productUrl')


credentials = authenticate(credentials_path)
photo_url = search_photos(credentials, search_word)

if photo_url:
    print(f"Фото с ключевым словом '{search_word}': {photo_url}")
else:
    print(f"Фото с ключевым словом '{search_word}' не найдено.")