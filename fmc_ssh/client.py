import paramiko
import time
from typing import Optional, Tuple

class FMCSSHClient:
    """Client to handle SSH interaction with FMC server."""

    def __init__(self, host: str, password: str, user: str = "admin"):
        self.host = host
        self.user = user
        self.password = password
        self.client = None
        self.channel = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.user, password=self.password)
        self.channel = self.client.invoke_shell()
        self._wait_for_prompt('>')
        self.channel.send('expert\n')
        self._wait_for_prompt(':~$')
        self.channel.send('sudo su -\n')
        self._wait_for_prompt('Password:')
        self.channel.send(self.password + '\n')
        self._wait_for_prompt(':~#')

    def _wait_for_prompt(self, prompt: str, timeout: int = 30) -> str:
        buff = ''
        start = time.time()
        while not buff.strip().endswith(prompt):
            if self.channel.recv_ready():
                buff += self.channel.recv(1024).decode('utf-8')
            if time.time() - start > timeout:
                raise TimeoutError(f'Timeout waiting for prompt: {prompt}')
            time.sleep(0.1)
        return buff

    def run_command(self, command: str) -> str:
        self.channel.send(command + '\n')
        output = self._wait_for_prompt(':~#')
        return output

    def close(self):
        if self.client:
            self.client.close()


    def interactive_shell(self):
        try:
            while True:
                cmd = input('fmc# ')
                if cmd.strip().lower() in ('exit', 'quit'):
                    break
                output = self.run_command(cmd)
                print(output, end='')
        finally:
            self.close()
