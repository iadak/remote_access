import sys
import os
import types
import unittest
from unittest.mock import MagicMock, patch

# Provide a simple pexpect stub so tests can run without the real dependency.
pexpect_stub = types.ModuleType("pexpect")
pexpect_stub.spawn = MagicMock()
pexpect_stub.exceptions = types.SimpleNamespace(EOF=Exception, TIMEOUT=Exception)
sys.modules.setdefault("pexpect", pexpect_stub)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fmc_ssh.client import FMCSSHClient


class TestFMCSSHClient(unittest.TestCase):
    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            FMCSSHClient('', 'pass')
        with self.assertRaises(ValueError):
            FMCSSHClient('host', '')

    def test_run_command_strips_prompt(self):
        client = FMCSSHClient('1.2.3.4', 'pass', session=MagicMock())
        client.prompt = ''
        client._send_and_wait = MagicMock(return_value='out\nroot@host:~# ')
        result = client.run_command('ls')
        client._send_and_wait.assert_called_with('ls', ':~#')
        self.assertEqual(result, 'out\n')
        self.assertEqual(client.prompt, 'root@host:~#')

    def test_context_manager_calls_connect_and_close(self):
        client = FMCSSHClient('1.2.3.4', 'pass', session=MagicMock())
        client.connect = MagicMock()
        client.close = MagicMock()
        with client as c:
            self.assertIs(c, client)
            client.connect.assert_called_once()
        client.close.assert_called_once()

    def test_connect_uses_given_port(self):
        with patch('fmc_ssh.client.pexpect.spawn') as spawn:
            spawn.return_value = MagicMock()
            client = FMCSSHClient('1.2.3.4', 'pass', port=2222)
            client._wait_for_prompt = MagicMock()
            client._send_and_wait = MagicMock()
            client.connect()
            spawn.assert_called_with('ssh admin@1.2.3.4 -p 2222', encoding='utf-8', timeout=30)


if __name__ == '__main__':
    unittest.main()
