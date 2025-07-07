## List of prompts used to develop this project using Codex

### Prompt 1
This repo is currently empty. I would like you to initialise a Python project that should have a script which can connect to a FMC server via SSH. Assume that the username is "admin" while the password will be provided as an argument to the script. Since the code requires to connect to a remote server, a server IP addresses will also be required to be passed to the script. Optionally a command will also be passed to the script.

Once the connection is established the system will provide a prompt like the following ```>```. Then, the script should automatically enter "expert" and send it to the remote server which should return a prompt ending with ```:~$```. On this prompt, the script should automatically enter ```sudo su -``` and send it to the server and expect a prompt like ```Password: ```. The script should automatically enter the password that was passed as an argument and send it to the server. At the point, the server returns a prompt ending with ```:~#```.

Please recall that we had passed an optional ```command``` argument. If the argument is provided, execute the argument, capture the stdout / stderr and print on the console. Then close the session.

If the argument is not provided, then provide an interactive shell where we can run commands and print the responses on the console. Continue this till the session is active.

Please remember the following while implementing.
* This being the very first implementation, you can create a script. However, make the script modularised because we will continuously iterate on the design. There should be a main script that executes the backend logic and the backend logic can be implemented to provide APIs/functions.
* We would like to keep it modularised because the APIs / functions can later be exposed in a way so that they could be called via external systems or used as Agent tools. But, please note that we do not want to implement everything in the beginning. Treat this is an iterative project with extensible design so that we can adopt the script for larger use cases.
* Provide long and short command-line options using ArgumentParser
* Provide help options to print the command-line usage
* Use Python as implementation language

I understand that it is a substantial set of requirements to initiate the repo. I hope you will do a good job with it.

### Prompt 2
Check the project and find places for improvement. Please inspect the code with emphasis on code structure, input / output validation, error handling, testability, code duplication and overall robustness.

### Prompt 3
Right now the code works with an assumption that the SSH port to the server has a fixed value of 22. However, it may be possible that the server could be behind a NAT and the SSH port may be forwarded as a different port number. So, please re-factor the code to allow for an optional port number field. If the port number is omitted, assume 22 as default value. Please ensure that you would be making incremental code changes by keeping the existing design, syntax and flow of code intact.

### Prompt 4
I changed my mind. Since password can have special characters, we could have issues passing the password in a command-line. Assume that Password will be configured as a field called "password" in a properties file called ```config/app.properties```. Throw an error if the field is not populated. Do not pass ```password``` any more in the command-line. Provide the details about the config in the help option of the script. Can you do it?

### Prompt 5
Did you not need to change the test client code? Also, can you please change the config file from ```app.properties``` to ```remote_access.properties```?

### Prompt 6
Looks like the current code appends its own prompt ```fmc#``` and overwrites the prompt received from the server. Actually, response to every command is received from the server and the server prompt is appended at the end of response. The code should extract the prompt from the response and use it for accepting new commands instead of using its own. This prompt may look like ```<user>@<host>:~#```. The prompt is separated from the response of the command by a. new line. Can you refactor the code to extract this prompt and print it in the console so that the next command against this prompt? You can leave a space after displaying the prompt for better readability of the commands. Please ensure to remove the existing prompt ```fmc#```


