# remote_access

This repository provides a simple Python utility to connect to a Firepower Management Center (FMC) server over SSH.

## Requirements

- Python 3.8+
- [`pexpect`](https://pypi.org/project/pexpect/) library

## Usage

```
python -m fmc_ssh.main -s <SERVER_IP> [-P <PORT>] [-c <COMMAND>]
```

- `-s`, `--server` – IP address of the FMC server.
- The password for the `admin` user is read from `config/remote_access.properties`.
- `-P`, `--port` – SSH port number if not 22.
- `-c`, `--command` – optional command to run after obtaining root shell. If omitted, an interactive shell is opened.

Create a file `config/remote_access.properties` alongside the code with a line like:

```
password=YOUR_PASSWORD
```

The script logs in as `admin`, enters expert mode and elevates to root automatically. When a command is supplied, its output is printed and the session closes. Without a command, an interactive prompt is provided until you type `exit` or press `Ctrl-C`.

You can also use the client as a context manager:

```python
from fmc_ssh import FMCSSHClient

with FMCSSHClient("10.0.0.1", "p@ssw0rd", port=22) as client:
    print(client.run_command("ls"))
```

Usage (Edit [config](config/remote_access.properties) to update ```password```)
```
(venv) IADAK-M-WV4X:remote_access iadak$ python3 fmc_ssh/main.py -s u32c01p10-vrouter.cisco.com -P 12502
root@firepower:~# fmc# grep MODEL /etc/sf/ims.conf
grep MODEL /etc/sf/ims.conf
UPGRADE_PULL_DISABLE_FOR_MODELS="63 66 69 72"
MODEL_CLASS="Defense Center"
MODELNUMBER=66
MODEL="Cisco Secure Firewall Management Center for VMware"
MODEL_TYPE=CONSOLE
MODELID=E
FAC_MODEL_ID=T
root@firepower:~# fmc# 
```
