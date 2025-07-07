import argparse
import sys

from .client import FMCSSHClient


def parse_args():
    parser = argparse.ArgumentParser(description="Connect to FMC server via SSH")
    parser.add_argument('-s', '--server', required=True, help='FMC server IP address')
    parser.add_argument('-p', '--password', required=True, help='Password for admin user')
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
        with FMCSSHClient(args.server, args.password) as client:
            if args.command:
                output = client.run_command(args.command)
                print(output, end='')
            else:
                client.interactive_shell()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)


if __name__ == '__main__':
    main()

