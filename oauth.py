# -*- coding: utf-8 -*-
import json
import os

import flask
import time
import httplib2
import random
import datetime

import google.oauth2.credentials
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

MAX_RETRIES = 10

# 这个是凭据里的OAuth2客户端配置信息json
CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtubepartner',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
app.secret_key = "这里填写凭据里的API密钥"


@app.route('/')
def index():
    print("enter index....")
    return flask.redirect('authorize')


@app.route('/authorize')
def authorize():
    print("enter authorize....")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True, _scheme='https')
    print("authorize redirect_uri:", flow.redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    flask.session['state'] = state

    print("authorize authorization_url:", authorization_url)

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    print("enter oauth2callback....")
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True, _scheme='https')
    print("oauth2callback redirect_uri:", flow.redirect_uri)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)


    credentials = flow.credentials
    saved_credentials = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    saved_credentials['token'] = refresh_token(saved_credentials)

    flask.session['credentials'] = saved_credentials

    print(json.dumps(saved_credentials, indent=4, ensure_ascii=False))

    creds = json.dumps(saved_credentials, separators=(',', ':'), ensure_ascii=False)
    with open("credentials.txt", "w", encoding="utf-8") as file:
        file.write(creds)

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    client = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)


    return channels_list_by_username(client, part='snippet,contentDetails,statistics', forUsername='GoogleDevelopers')


def channels_list_by_username(client, **kwargs):
    response = client.channels().list(
        **kwargs
    ).execute()

    return flask.jsonify(**response)



if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('0.0.0.0', 8090, debug=True)
