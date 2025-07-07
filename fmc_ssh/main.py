import argparse
import sys
import os
from typing import Dict

# General purpose routine for getting the script location
# This function can be used to set any of the folders / files referenced in this script
# relative to the script location
def get_script_dir():
    """Get the directory in which the script resides."""
    script_dir = os.path.split(__file__)[0]
    if '' == script_dir:
        script_dir = os.getcwd()

    return os.path.abspath(script_dir)

# General purpose routine for getting the script name
def get_script_name():
    """Get the name of this script."""
    return os.path.split(__file__)[1]

# Set up files and directories relative to the location of the script
script_dir = get_script_dir()
script_root_dir = os.path.join(script_dir, '..')

# Add the script root directory to the system path
if script_root_dir not in sys.path:
    sys.path.insert(0, script_root_dir)

from fmc_ssh.client import FMCSSHClient

# Default configuration file location
CONFIG_FILE = os.path.join(script_root_dir, "config", "remote_access.properties")


def load_password(config_path: str = CONFIG_FILE) -> str:
    """Load the admin password from a properties file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    properties: Dict[str, str] = {}
    with open(config_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            properties[key.strip()] = value.strip()

    password = properties.get("password")
    if not password:
        raise ValueError("Password not specified in config file")
    return password

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Connect to FMC server via SSH. The admin password is read from "
            "config/remote_access.properties (field 'password')."
        )
    )
    parser.add_argument('-s', '--server', required=True, help='FMC server IP address')
    parser.add_argument('-P', '--port', type=int, default=22, help='SSH port number (default 22)')
    parser.add_argument('-c', '--command', help='Command to run on the server')
    args = parser.parse_args()
    if not FMCSSHClient._is_valid_host(args.server):  # type: ignore[attr-defined]
        parser.error('Invalid server address')
    return args


def main():
    args = parse_args()
    try:
        password = load_password()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return
    try:
        with FMCSSHClient(args.server, password, port=args.port) as client:
            if args.command:
                output = client.run_command(args.command)
                print(output, end='')
            else:
                client.interactive_shell()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)


if __name__ == '__main__':
    main()