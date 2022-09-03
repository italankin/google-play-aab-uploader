import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import jwt
import requests

ACCESS_TOKEN_LIFESPAN = timedelta(minutes=10)
EDIT_ID_LIFESPAN = timedelta(minutes=10)
REQUESTS_TIMEOUT = 300


def check_response(response: requests.Response):
    if not response.ok:
        print(
            (f'FAILED: \'{response.request.method} {response.request.url}\' failed '
             f'with HTTP {response.status_code}:\n{response.text}'),
            file=sys.stderr)
        exit(1)


def obtain_access_token(key_path: str) -> str:
    print('obtaining access token...')
    with open(key_path) as f:
        key_file = json.load(f)
    exp = datetime.now() + ACCESS_TOKEN_LIFESPAN
    claim_set = {
        'iss': key_file['client_email'],
        'scope': 'https://www.googleapis.com/auth/androidpublisher',
        'aud': 'https://oauth2.googleapis.com/token',
        'exp': exp.strftime('%s'),
        'iat': datetime.now().strftime('%s')
    }
    private_key = key_file['private_key'].encode('utf-8')
    assertion = jwt.encode(
        payload=claim_set,
        key=private_key,
        algorithm='RS256',
        headers={'alg': 'RS256', 'typ': 'JWT'})
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': assertion
    }
    response = requests.post(
        url='https://oauth2.googleapis.com/token',
        data=data,
        timeout=REQUESTS_TIMEOUT)
    check_response(response)
    access_token = response.json()['access_token']
    print(f'obtained access_token: ****({len(access_token)})')
    return access_token


def obtain_edit_id(access_token: str, package_name: str) -> str:
    print('obtaining edit_id...')
    expiry_time = (datetime.now() + EDIT_ID_LIFESPAN).strftime('%s')
    app_edit = {
        'expiryTimeSeconds': expiry_time
    }
    response = requests.post(
        url=f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/edits',
        json=app_edit,
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=REQUESTS_TIMEOUT)
    check_response(response)
    edit_id = response.json()['id']
    print(f'obtained {edit_id=}')
    return edit_id


def upload_aab(access_token: str, aab_path: str, package_name: str, edit_id: str):
    print('uploading aab...')
    with open(aab_path, 'rb') as f:
        data = f.read()
    response = requests.post(
        url=f'https://androidpublisher.googleapis.com/upload/androidpublisher/v3/applications/{package_name}/edits/{edit_id}/bundles',
        data=data,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        },
        timeout=REQUESTS_TIMEOUT
    )
    check_response(response)
    uploaded_bundle = response.json()
    version_code = uploaded_bundle['versionCode']
    sha256 = uploaded_bundle['sha256']
    print(f'successfully uploaded aab: {version_code=}, {sha256=}')


def commit_edit(access_token: str, package_name: str, edit_id: str):
    print(f'commiting {edit_id=}...')
    response = requests.post(
        url=f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/edits/{edit_id}:commit',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=REQUESTS_TIMEOUT)
    check_response(response)
    print(f'committed {edit_id=}')


def main():
    parser = argparse.ArgumentParser(description="Google Play AAB uploader")
    parser.add_argument(
        '--key-path',
        type=str,
        required=True,
        dest='key_path',
        help='Path to service account key file')
    parser.add_argument(
        '--package-name',
        type=str,
        required=True,
        dest='package_name',
        help='Package name of an app')
    parser.add_argument(
        '--aab-path',
        type=str,
        required=True,
        dest='aab_path',
        help='Path to app bundle file')
    args = parser.parse_args()
    if not os.path.exists(args.key_path):
        print(f'key file does not exist: {args.key_path}', file=sys.stderr)
        exit(1)
    if not os.path.exists(args.aab_path):
        print(f'aab file does not exist: {args.aab_path}', file=sys.stderr)
        exit(1)
    access_token = obtain_access_token(args.key_path)
    edit_id = obtain_edit_id(access_token, args.package_name)
    upload_aab(access_token, args.aab_path, args.package_name, edit_id)
    commit_edit(access_token, args.package_name, edit_id)
    print('done')


if __name__ == "__main__":
    main()
