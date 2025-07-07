# remote_access

This repository provides a simple Python utility to connect to a Firepower Management Center (FMC) server over SSH.

## Requirements

- Python 3.8+
- [`paramiko`](https://pypi.org/project/paramiko/) library

## Usage

```
python -m fmc_ssh.main -s <SERVER_IP> -p <PASSWORD> [-c <COMMAND>]
```

- `-s`, `--server` – IP address of the FMC server.
- `-p`, `--password` – password for the `admin` user.
- `-c`, `--command` – optional command to run after obtaining root shell. If omitted, an interactive shell is opened.

The script logs in as `admin`, enters expert mode and elevates to root automatically. When a command is supplied, its output is printed and the session closes. Without a command, an interactive prompt is provided until you type `exit` or `quit`.

