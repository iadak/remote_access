import sys
import types
import os
import unittest
from unittest.mock import MagicMock

# Provide a simple paramiko stub so tests can run without the real dependency.
paramiko_stub = types.ModuleType("paramiko")
paramiko_stub.AutoAddPolicy = object
class _SSHClient:
    def set_missing_host_key_policy(self, *a, **kw):
        pass
    def connect(self, *a, **kw):
        pass
    def invoke_shell(self, *a, **kw):
        return MagicMock()
paramiko_stub.SSHClient = _SSHClient
sys.modules.setdefault("paramiko", paramiko_stub)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fmc_ssh.client import FMCSSHClient


class TestFMCSSHClient(unittest.TestCase):
    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            FMCSSHClient('', 'pass')
        with self.assertRaises(ValueError):
            FMCSSHClient('host', '')

    def test_run_command_strips_prompt(self):
        client = FMCSSHClient('1.2.3.4', 'pass', ssh_client=MagicMock())
        client.prompt = ''
        client._send_and_wait = MagicMock(return_value='out\nroot@host:~# ')
        result = client.run_command('ls')
        client._send_and_wait.assert_called_with('ls', ':~#')
        self.assertEqual(result, 'out\n')
        self.assertEqual(client.prompt, 'root@host:~#')

    def test_context_manager_calls_connect_and_close(self):
        client = FMCSSHClient('1.2.3.4', 'pass', ssh_client=MagicMock())
        client.connect = MagicMock()
        client.close = MagicMock()
        with client as c:
            self.assertIs(c, client)
            client.connect.assert_called_once()
        client.close.assert_called_once()

    def test_connect_uses_given_port(self):
        ssh_client = MagicMock()
        ssh_client.invoke_shell.return_value = MagicMock()
        client = FMCSSHClient('1.2.3.4', 'pass', port=2222, ssh_client=ssh_client)
        client._wait_for_prompt = MagicMock()
        client._send_and_wait = MagicMock()
        client.connect()
        ssh_client.connect.assert_called_with(hostname='1.2.3.4', username='admin', password='pass', port=2222)


if __name__ == '__main__':
    unittest.main()
