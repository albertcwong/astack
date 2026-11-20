import base64
import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / 'skills/sonarqube-code-quality/scripts/sonar.py'
spec = importlib.util.spec_from_file_location('sonar', PATH)
sonar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sonar)


class SonarTests(unittest.TestCase):
    def invoke(self, *args, payload=b'{}'):
        with patch.object(sys, 'argv', ['sonar', *args]), patch.object(
            sonar, 'config', return_value=('https://example.org/sonar', 'test')
        ), patch.object(sonar, 'credential', return_value='test-token'), patch.object(
            sonar, 'build_opener'
        ) as opener, contextlib.redirect_stdout(io.StringIO()) as out:
            opener.return_value.open.return_value.__enter__.return_value.read.return_value = payload
            sonar.main()
            return out.getvalue(), opener.return_value.open.call_args.args[0]

    def test_timeout_uses_only_matching_environment_token(self):
        url = 'https://example.org/sonar'
        with patch.object(sys, 'platform', 'linux'), patch.object(
            sonar.subprocess, 'run', side_effect=sonar.subprocess.TimeoutExpired('secret-tool', 15)
        ), patch.dict(sonar.os.environ, {'SONARQUBE_TOKEN': 'fixture'}, clear=True):
            self.assertIsNone(sonar.credential(url, url))
            sonar.os.environ['SONARQUBE_TOKEN_URL'] = 'https://other.example'
            self.assertIsNone(sonar.credential(url, url))
            sonar.os.environ['SONARQUBE_TOKEN_URL'] = url
            self.assertEqual(sonar.credential(url, url), 'fixture')

    def test_quality_gate_scopes_and_encodes_branch(self):
        out, req = self.invoke('get', 'qualitygates/project_status', 'projectKey=demo', 'branch=a&b')
        self.assertEqual(req.full_url, 'https://example.org/sonar/api/qualitygates/project_status?projectKey=demo&branch=a%26b')
        self.assertEqual(req.get_header('Authorization'), 'Basic ' + base64.b64encode(b'test-token:').decode('ascii'))
        self.assertNotIn('test-token', out)

    def test_triage_uses_form_body(self):
        _, req = self.invoke('post', 'issues/add_comment', 'issue=123', 'text=Triaged via pi')
        self.assertEqual(req.data, b'issue=123&text=Triaged+via+pi')

    def test_validate_requires_boolean_true(self):
        output, req = self.invoke('validate', payload=b'{"valid":true}')
        self.assertEqual(output, 'VALID\n')
        self.assertEqual(req.get_header('Authorization'), 'Basic ' + base64.b64encode(b'test-token:').decode('ascii'))
        self.assertNotIn('test-token', req.full_url)
        self.assertNotIn('test-token', output)
        with self.assertRaisesRegex(SystemExit, 'not valid'):
            self.invoke('validate', payload=b'{"valid":false}')

    def test_admin_write_is_rejected(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.invoke('post', 'system/restart')

    def test_redirect_not_followed(self):
        self.assertIsNone(sonar.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://elsewhere.test'))
