import ipaddress
import logging
import re
from typing import Optional

import pexpect

class FMCSSHClient:
    """Client to handle SSH interaction with an FMC server."""

    def __init__(
        self,
        host: str,
        password: str,
        user: str = "admin",
        port: int = 22,
        session: Optional[pexpect.spawn] = None,
    ) -> None:
        if not host or not self._is_valid_host(host):
            raise ValueError("Invalid host provided")
        if not password:
            raise ValueError("Password must be provided")

        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.session: Optional[pexpect.spawn] = session
        self.prompt = ""
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
        try:
            if not self.session:
                cmd = f"ssh {self.user}@{self.host} -p {self.port}"
                self.session = pexpect.spawn(cmd, encoding="utf-8", timeout=30)
            self._wait_for_prompt("assword:")
            self.session.sendline(self.password)
            self._wait_for_prompt(">")
            self._send_and_wait("expert", ":~$")
            self._send_and_wait("sudo su -", "Password:")
            output = self._send_and_wait(self.password, ":~#")
            self.prompt = self._extract_prompt(output)
            logger.debug("Connected to %s", self.host)
        except (pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT) as exc:
            logger.error("SSH connection failed: %s", exc)
            self.close()
            raise ConnectionError(f"Failed to connect to {self.host}") from exc

    def _send_and_wait(self, command: str, prompt: str) -> str:
        """Send a command and wait for the given prompt."""
        if not self.session:
            raise RuntimeError("SSH session is not open")
        self.session.sendline(command)
        return self._wait_for_prompt(prompt)

    def _wait_for_prompt(self, prompt: str, timeout: int = 30) -> str:
        if not self.session:
            raise RuntimeError("SSH session is not open")
        self.session.expect(prompt, timeout=timeout)
        return (self.session.before or "") + (self.session.after or "")

    @staticmethod
    def _extract_prompt(response: str) -> str:
        lines = response.rstrip().splitlines()
        return lines[-1] if lines else ""

    def run_command(self, command: str) -> str:
        response = self._send_and_wait(command, ':~#')
        self.prompt = self._extract_prompt(response)
        lines = response.rstrip().splitlines()
        return "\n".join(lines[:-1]) + "\n" if len(lines) > 1 else ""

    def close(self):
        if self.session:
            self.session.close()
        self.session = None


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

