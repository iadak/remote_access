import argparse
from .client import FMCSSHClient


def parse_args():
    parser = argparse.ArgumentParser(description="Connect to FMC server via SSH")
    parser.add_argument('-s', '--server', required=True, help='FMC server IP address')
    parser.add_argument('-p', '--password', required=True, help='Password for admin user')
    parser.add_argument('-c', '--command', help='Command to run on the server')
    return parser.parse_args()


def main():
    args = parse_args()
    client = FMCSSHClient(args.server, args.password)
    client.connect()
    if args.command:
        output = client.run_command(args.command)
        print(output, end='')
        client.close()
    else:
        client.interactive_shell()


if __name__ == '__main__':
    main()
