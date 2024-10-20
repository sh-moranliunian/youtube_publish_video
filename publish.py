#!/usr/bin/python

import argparse
import os
import datetime

import httplib2
import random
import time
import json

import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

def refresh_token(credentials_obj):
    creds = Credentials(
        None,
        refresh_token=credentials_obj['refresh_token'],
        client_id=credentials_obj['client_id'],
        client_secret=credentials_obj['client_secret'],
        token_uri=credentials_obj['token_uri']
    )

    # 刷新访问令牌
    creds.refresh(Request())

    # 获取新的访问令牌
    access_token = creds.token
    print("new access_token: \n", access_token)
    return access_token

def get_authenticated_service():
    file_path = "credentials.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    jsonObj = json.loads(content)

    jsonObj['token'] = refresh_token(jsonObj)

    credentials = google.oauth2.credentials.Credentials(**jsonObj)

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def initialize_upload(youtube, options):
    tags = None
    if options['keywords']:
        tags = options['keywords'].split(',')

    body = dict(
        snippet=dict(
            title=options['title'],
            description=options['description'],
            tags=tags,
            categoryId=options['category']
        ),
        status=dict(
            privacyStatus=options['privacyStatus']
        )
    )

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' % response['id'])
                else:
                    exit('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)


if __name__ == '__main__':
    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y%m%d%H%M%S")
    print("formatted_time: \n", formatted_time)

    title = f"这是yumenzhisi的测试视频 {formatted_time}"

    options = {
        "file": "data/yaya.mp4",
        "title": title,
        "description": "Test Description",
        "category": "22",
        "keywords": "Video keywords, comma separated",
        "privacyStatus": "public"
    }

    youtube = get_authenticated_service()

    try:
        initialize_upload(youtube, options)
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
