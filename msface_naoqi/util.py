#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: util.py
Description: Shared utilities for the Python SDK of the Cognitive Face API.
"""
import os.path
import time

import requests

import face_api_naoqi as CF

_BASE_URL = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'
TIME_SLEEP = 1


class CognitiveFaceException(Exception):
    """Custom Exception for the python SDK of the Cognitive Face API.

    Attributes:
        status_code: HTTP response status code.
        code: error code.
        msg: error message.
    """
    def __init__(self, status_code, code, msg):
        super(CognitiveFaceException, self).__init__()
        self.status_code = status_code
        self.code = code
        self.msg = msg

    def __str__(self):
        return (
            'Error when calling Cognitive Face API:\n'
            '\tstatus_code: {}\n'
            '\tcode: {}\n'
            '\tmessage: {}\n'
        ).format(self.status_code, self.code, self.msg)


class Key(object):
    """Manage Subscription Key."""

    @classmethod
    def set(cls, key):
        """Set the Subscription Key."""
        cls.key = key

    @classmethod
    def get(cls):
        """Get the Subscription Key."""
        if not hasattr(cls, 'key'):
            cls.key = None
        return cls.key


def request(method, url, data=None, json=None, headers=None, params=None):
    # pylint: disable=too-many-arguments
    """Universal interface for request."""

    # Make it possible to call only with short name (without _BASE_URL).
    if not url.startswith('https://'):
        url = _BASE_URL + url

    # Setup the headers with default Content-Type and Subscription Key.
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    headers['Ocp-Apim-Subscription-Key'] = Key.get()

    response = requests.request(method, url, params=params, data=data,
                                json=json, headers=headers)

    # Handle result and raise custom exception when something wrong.
    result = None
    # `person_group.train` return 202 status code for success.
    if response.status_code not in (200, 202):
        print('status_code: {}'.format(response.status_code))
        print('response: {}'.format(response.text))
        error_msg = response.json()['error']
        raise CognitiveFaceException(
            response.status_code,
            error_msg.get('code'),
            error_msg.get('message'))

    # Prevent `reponse.json()` complains about empty response.
    if response.text:
        result = response.json()
    else:
        result = {}

    return result


def parse_image(image):
    """Parse the image smartly and return metadata for request.

    First check whether the image is a URL or a file path or a file-like object
    and return corresponding metadata.

    Args:
        image: A URL or a file path or a file-like object represents an image.

    Returns:
        a three-item tuple consist of HTTP headers, binary data and json data
        for POST.
    """
    if hasattr(image, 'read'):  # When image is a file-like object.
        headers = {'Content-Type': 'application/octet-stream'}
        data = image.read()
        return headers, data, None
    elif os.path.isfile(image):  # When image is a file path.
        headers = {'Content-Type': 'application/octet-stream'}
        data = open(image, 'rb').read()
        return headers, data, None
    else:  # Defailt treat it as a URL (string).
        headers = {'Content-Type': 'application/json'}
        json = {'url': image}
        return headers, None, json


def wait_for_training(person_group_id):
    """Wait for the finish of person_group training."""
    idx = 1
    while True:
        res = CF.person_group.get_status(person_group_id)
        if res['status'] in ('succeeded', 'failed'):
            break
        print('The training of Person Group {} is onging: #{}'.format(
            person_group_id, idx))
        time.sleep(2**idx)
        idx += 1


def clear_face_lists():
    """[Dangerous] Clear all the face lists and all related persisted data."""
    face_lists = CF.face_list.lists()
    time.sleep(TIME_SLEEP)
    for face_list in face_lists:
        face_list_id = face_list['faceListId']
        CF.face_list.delete(face_list_id)
        print('Deleting Face List {}'.format(face_list_id))
        time.sleep(TIME_SLEEP)


def clear_person_groups():
    """[Dangerous] Clear all the person gourps and all related persisted data.
    """
    person_groups = CF.person_group.lists()
    time.sleep(TIME_SLEEP)
    for person_group in person_groups:
        person_group_id = person_group['personGroupId']
        CF.person_group.delete(person_group_id)
        print('Deleting Person Group {}'.format(person_group_id))
        time.sleep(TIME_SLEEP)
