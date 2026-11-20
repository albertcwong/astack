"""Small SonarQube Web API client. Credentials stay in this process."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request

CONFIG = Path.home() / '.config/astack/sonarqube.json'
READ = {'components/search', 'measures/component', 'measures/component_tree',
        'measures/search_history', 'qualitygates/project_status', 'issues/search',
        'hotspots/search', 'hotspots/show', 'authentication/validate'}
WRITE = {'issues/do_transition', 'issues/add_comment', 'hotspots/change_status'}
KEY = 'SONARQUBE_TOKEN'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def config():
    data = json.loads(CONFIG.read_text())
    url = data['url'].rstrip('/')
    parts = urlsplit(url)
    if (parts.scheme != 'https' or not parts.hostname or parts.username is not None
            or parts.query or parts.fragment):
        raise ValueError('Configure a trusted HTTPS server URL without credentials, query or fragment')
    return url, data.get('keyring_service', url)


def credential(url, service):
    if sys.platform == 'darwin':
        cmd = ['/usr/bin/security', 'find-generic-password', '-s', service, '-a', KEY, '-w']
    elif sys.platform.startswith('linux'):
        cmd = ['secret-tool', 'lookup', 'service', service, 'username', KEY]
    else:
        cmd = None
    if cmd:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    if os.environ.get('SONARQUBE_TOKEN_URL', '').rstrip('/') == url:
        return os.environ.get(KEY)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'validate', 'get', 'post'])
    parser.add_argument('endpoint', nargs='?')
    parser.add_argument('fields', nargs='*', metavar='name=value')
    args = parser.parse_args()
    url, service = config()
    token = credential(url, service)
    if args.action == 'status':
        print('PRESENT' if token else 'MISSING')
        return
    if not token:
        sys.exit('No token. Use generate-sonarqube-token.')
    endpoint = 'authentication/validate' if args.action == 'validate' else args.endpoint
    post = args.action == 'post'
    if endpoint not in (WRITE if post else READ):
        parser.error('unsupported endpoint for this method')
    if any('=' not in field for field in args.fields):
        parser.error('expected name=value')
    fields = urlencode([tuple(field.split('=', 1)) for field in args.fields])
    target = url + '/api/' + endpoint
    # Token-as-username authentication also works on servers without Bearer support.
    authorization = base64.b64encode((token + ':').encode('utf-8')).decode('ascii')
    req = Request(target + ('?' + fields if fields and not post else ''),
                  data=fields.encode() if post else None,
                  headers={'Authorization': 'Basic ' + authorization})
    with build_opener(NoRedirect()).open(req, timeout=30) as response:
        body = response.read()
    if args.action == 'validate':
        if json.loads(body).get('valid') is not True:
            sys.exit('Token is not valid')
        print('VALID')
    elif body:
        print(json.dumps(json.loads(body), ensure_ascii=True))


if __name__ == '__main__':
    try:
        main()
    except HTTPError as error:
        sys.exit(f'SonarQube returned HTTP {error.code}')
    except (OSError, ValueError, KeyError, URLError, subprocess.TimeoutExpired) as error:
        sys.exit(f'SonarQube setup or request failed ({type(error).__name__}); check {CONFIG} and connectivity')
