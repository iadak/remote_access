import ipaddress
import logging
import re
import time
from typing import Optional

import paramiko

class FMCSSHClient:
    """Client to handle SSH interaction with an FMC server."""

    def __init__(
        self,
        host: str,
        password: str,
        user: str = "admin",
        port: int = 22,
        ssh_client: Optional[paramiko.SSHClient] = None,
    ) -> None:
        if not host or not self._is_valid_host(host):
            raise ValueError("Invalid host provided")
        if not password:
            raise ValueError("Password must be provided")

        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.client: paramiko.SSHClient = ssh_client or paramiko.SSHClient()
        self.channel = None
        self.prompt = ""
        self.command_timeout = self._get_command_timeout()
        self.inactivity_timeout = self._get_inactivity_timeout()
        logging.getLogger(__name__).debug("FMCSSHClient initialised for %s", host)

    def __enter__(self) -> "FMCSSHClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def _is_valid_host(value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return re.match(r"^[a-zA-Z0-9.-]+$", value) is not None

    def connect(self) -> None:
        """Open the SSH connection and elevate to root."""
        logger = logging.getLogger(__name__)
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(hostname=self.host, username=self.user, password=self.password, port=self.port)
            self.channel = self.client.invoke_shell()
            self._wait_for_prompt('>')
            self._send_and_wait('expert', ':~$')
            self._send_and_wait('sudo su -', 'Password:')
            output = self._send_and_wait(self.password, ':~#')
            self.prompt = self._extract_prompt(output)
            logger.debug("Connected to %s", self.host)
        except paramiko.SSHException as exc:
            logger.error("SSH connection failed: %s", exc)
            self.close()
            raise ConnectionError(f"Failed to connect to {self.host}") from exc

    def _send_and_wait(self, command: str, prompt: str) -> str:
        """Send a command and wait for the given prompt."""
        if not self.channel:
            raise RuntimeError("SSH channel is not open")
        self.channel.send(command + "\n")
        return self._wait_for_prompt(prompt)

    def _wait_for_prompt(self, prompt: str, timeout: int = 30) -> str:
        if not self.channel:
            raise RuntimeError("SSH channel is not open")
        buff = ""
        start = time.time()
        while not buff.strip().endswith(prompt):
            if self.channel.recv_ready():
                buff += self.channel.recv(1024).decode("utf-8")
            if time.time() - start > timeout:
                raise TimeoutError(f"Timeout waiting for prompt: {prompt}")
            time.sleep(0.1)
        return buff

    @staticmethod
    def _extract_prompt(response: str) -> str:
        lines = response.rstrip().splitlines()
        return lines[-1] if lines else ""

    def _get_command_timeout(self) -> int:
        try:
            import configparser
            import os
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'remote_access.properties')
            if os.path.exists(config_path):
                config.read(config_path)
                return int(config.get('DEFAULT', 'command_timeout', fallback='30'))
        except Exception:
            pass
        return 30

    def _get_inactivity_timeout(self) -> int:
        try:
            import configparser
            import os
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'remote_access.properties')
            if os.path.exists(config_path):
                config.read(config_path)
                return int(config.get('DEFAULT', 'inactivity_timeout', fallback='30'))
        except Exception:
            pass
        return 30

    def run_command(self, command: str) -> str:
        import sys
        import select
        if not self.channel:
            raise RuntimeError("SSH channel is not open")
        self.channel.send(command + "\n")
        buff = ""
        start = time.time()
        prompt = ':~#'
        timeout = self.command_timeout
        inactivity_timeout = self.inactivity_timeout
        last_data_time = time.time()
        while True:
            data_received = False
            while self.channel.recv_ready():
                data = self.channel.recv(1024).decode("utf-8")
                print(data, end='', flush=True)
                buff += data
                data_received = True
                last_data_time = time.time()
                # Check if last non-empty line ends with prompt
                lines = buff.rstrip().splitlines()
                non_empty_lines = [line for line in lines if line.strip()]
                if non_empty_lines and non_empty_lines[-1].strip().endswith(prompt):
                    return "\n".join(lines[:-1]) + "\n" if len(lines) > 1 else ""
            # Allow user to send input if needed (for interactive commands)
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                user_input = sys.stdin.readline()
                self.channel.send(user_input)
                last_data_time = time.time()
            if not data_received:
                # Final prompt check after inactivity
                lines = buff.rstrip().splitlines()
                non_empty_lines = [line for line in lines if line.strip()]
                if non_empty_lines and non_empty_lines[-1].strip().endswith(prompt):
                    break
                if time.time() - last_data_time > inactivity_timeout:
                    break
            if time.time() - start > timeout:
                print(f"\nError: Timeout waiting for command to complete (>{timeout}s)")
                break
            time.sleep(0.1)
        self.prompt = self._extract_prompt(buff)
        lines = buff.rstrip().splitlines()
        return "\n".join(lines[:-1]) + "\n" if len(lines) > 1 else ""

    def close(self):
        if self.client:
            self.client.close()
        self.channel = None


    def interactive_shell(self):
        try:
            while True:
                prompt = f"{self.prompt} " if self.prompt else ""
                cmd = input(prompt)
                if cmd.strip().lower() in ('exit', 'quit'):
                    break
                if not cmd.strip():
                    continue
                output = self.run_command(cmd)
                print(output, end='')
        except KeyboardInterrupt:
            print()

