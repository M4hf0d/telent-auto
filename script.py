import telnetlib
import getpass
import sys
from time import sleep
import re


# Define the Telnet server's address and port
host = "127.0.0.1"
port = 5002  #5002 -> R3 5001 -> R2   # Default Telnet port

def exit_script():
        print("")
        print("")
        print("Terminating the script execution. Sending 'exit' and closing the connection....")
        sleep(2)
        ctrl_c = chr(3)  # ASCII code for Ctrl+C
        tn.write(ctrl_c.encode('ascii'))
        sleep(1)
        output = tn.read_very_eager().decode('ascii')
        print(output, end="")  # Print the output as it's received
        tn.write(b"\r")
        sleep(1)
        tn.write(b"exit\r")
        sleep(1)
        tn.close()
        sys.exit(0)



# Create a Telnet connection
try:
    tn = telnetlib.Telnet(host, port)
except ConnectionRefusedError:
    print("Connection refused. Check the server address and port.")
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
else:
    print("Connected to the Telnet server.")
    # Wait for the router to finish booting
    boot_complete = False
    while not boot_complete:
        output = tn.read_very_eager().decode('ascii')
        print(output, end="")  # Print the output as it's received

        # Check if a prompt indicating the router is ready is found
        if re.search(r'R\d+#|\(config\)#|Username:', output):
            boot_complete = True
        else:
            sleep(1)
            tn.write(b"\r")


    tn.write(b"\r")
    sleep(1)
    tn.write(b"\r")
    sleep(1)

    # Check if login is required by looking for the "Username: " prompt
    login_prompt = tn.read_until(b"Username:", timeout=2).decode('ascii')
    logged_in = False
    if "Username:" in login_prompt:
        print("Login is required. Please enter your username and password.")
        # Login is required
        login_attempts = 0
        while logged_in == False: 
            if login_attempts > 2 :
                print("Login attempts exceeded")
                exit_script()
            try:
            # Login
                user = input("Username: ")
                password = getpass.getpass(prompt='Password: ', stream=None)

                tn.write(user.encode('ascii') + b"\r")
                sleep(1)
                tn.write(password.encode('ascii') + b"\r")
                sleep(2)

                output = tn.read_very_eager().decode('ascii')
                sleep(1)

                if re.search(r'R\d+#', output): # login successfull "R2#" is in output
                    logged_in = True
                else:
                    print("\n\nLogin attempt failed. Please try again.")
                    login_attempts += 1
            except KeyboardInterrupt: #stopping the script
                print("\nKeyboard interrupt received. Exiting the script.")
                exit_script()
    else: 
        print("No login required")
        sleep(1)


    # Specify the path to your text file containing commands
    file_path = "conf.txt"

    try:
        with open(file_path, "r") as file:
            commands = file.readlines()

        for command in commands:
            command = command.strip()
            tn.write(command.encode('ascii') + b'\r')
            sleep(1)
            while True:
                # Read the output
                output = tn.read_very_eager().decode('ascii')
                print(output, end="")  # Print the output as it's received

                # Check if "--More--" is in the output
                if "--More--" in output:
                    # Send an Enter keypress to continue
                    tn.write(b"\r")
                    sleep(0.1)  
                else:
                    break  # Exit the loop when "--More--" is no longer present

    except KeyboardInterrupt:
        sleep(1)
        exit_script()  # Exit the script gracefully

    sleep(1)
    tn.write(b"exit\r")
    sleep(1)
    tn.write(b"\r")

    tn.close()
