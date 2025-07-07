import argparse
import sys
import os

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

def parse_args():
    parser = argparse.ArgumentParser(description="Connect to FMC server via SSH")
    parser.add_argument('-s', '--server', required=True, help='FMC server IP address')
    parser.add_argument('-p', '--password', required=True, help='Password for admin user')
    parser.add_argument('-P', '--port', type=int, default=22, help='SSH port number (default 22)')
    parser.add_argument('-c', '--command', help='Command to run on the server')
    args = parser.parse_args()
    if not args.password.strip():
        parser.error('Password cannot be empty')
    if not FMCSSHClient._is_valid_host(args.server):  # type: ignore[attr-defined]
        parser.error('Invalid server address')
    return args


def main():
    args = parse_args()
    try:
        with FMCSSHClient(args.server, args.password, port=args.port) as client:
            if args.command:
                output = client.run_command(args.command)
                print(output, end='')
            else:
                client.interactive_shell()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)


if __name__ == '__main__':
    main()