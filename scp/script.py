import telnetlib
import getpass
import sys
from time import sleep
import re
import os
import argparse
import datetime




def display_help():
    print("Usage:")
    print("python script.py -c [CONFIG TXT FILE] -ip [IP ADDRESS] -port [PORT]")
    print("Options:")
    print("-c       Configuration text file path")
    print("-ip      IP address of the Telnet server (default: 127.0.0.1)")
    print("-port    Port number for the Telnet connection (default: 5002)")
    print("-port    Port number for the Telnet connection (default: 5002)")

    sys.exit(0)


def main():
    try:
        RESET = "\033[0m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        WHITE = "\033[97m"

        parser = argparse.ArgumentParser(description="Script for injecting configuration commands via Telnet")
        parser.add_argument('-c', '--config', type=str, required=True, help='Configuration text file path')
        parser.add_argument('-ip', '--ip_address', type=str, required=True, 
                        help='IP address for telnet connection')
        parser.add_argument('-port', '--port_number', type=int, default=5002, 
                        help='Port number for the Telnet connection (default: 5002)')
        
        parser.add_argument('-l', '--log', action='store_true', help="Flag to indicate if a log file should be created (default: False)")


        args = parser.parse_args()
        # Validate the configuration file path
        if not args.config.endswith('.txt'):
            print("Error: Configuration file must end with .txt")
            sys.exit(1)

        # Validate the IP address format using a regular expression
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        if not re.match(ip_pattern, args.ip_address):
            print("Error: Invalid IP address format")
            sys.exit(1)

        file_path = args.config
        host = args.ip_address
        port = args.port_number

        if args.log : 
            with open("script_log.txt", "a") as log_file:
                current_datetime = datetime.datetime.now()
                timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

                log_file.write(f"Script Execution Log - [{timestamp}] \n\n")
                log_file.write("------------------------------------------------------------\n")
                log_file.write(f"[{timestamp}] - Starting script execution. \n\n")




        def log_event(event_description, event_details):
            if args.log:
                with open("script_log.txt", "a") as log_file:

                    current_datetime = datetime.datetime.now()
                    timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

                    log_entry = f"[{timestamp}] - {event_description}\n{event_details}\n\n"

                    log_file.write(log_entry)


    


        def exit_script():
                if args.log: 
                    with open("script_log.txt", "a") as log_file:
                        log_file.write("------------------------------------------------------------\n")
                print("")
                print("")
                print("Terminating the script execution. Sending 'exit' and closing the connection....")
                sleep(2)
                ctrl_c = chr(3)  # ASCII code for Ctrl+C
                tn.write(ctrl_c.encode('ascii'))
                sleep(1)
                # output = tn.read_very_eager().decode('ascii')
                # print(output, end="")  # Print the output as it's received
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
            log_event(f"Connecting to Telnet server at {args.host} on port {args.port_number}.  \n - Connection refused. Check the server address and port.")

        except Exception as e:
            print(f"An error occurred: {e}")
            log_event(f"Connecting to Telnet server at {args.host} on port {args.port_number}.", f"\n - An error occurred: {e}")

            sys.exit(1)
        else:
            os.system('cls')
            print("Connected to the Telnet server.")
            log_event(f"Connecting to Telnet server at {args.ip_address} on port {args.port_number}.", f"\n   - Connection successful.")

            # Wait for the router to finish booting
            boot_complete = False
            while not boot_complete:
                output = tn.read_very_eager().decode('ascii')
                print("Still Booting, Please wait...")
                # print(output, end="")  # Print the output as it's received

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
            os.system('cls')
            login_prompt = tn.read_until(b"Username:", timeout=2).decode('ascii')
            logged_in = False
            if "Username:" in login_prompt:
                print("Login is required. Please enter your username and password.")
                # Login is required
                login_attempts = 0
                while logged_in == False: 
                    if login_attempts > 3 :
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
                            log_event(f"Loggin as '{user}'. ","- Login Successful")

                        else:
                            print("\n\nLogin attempt failed. Please try again.")
                            log_event(f"Loggin as '{user}'. ","- Login attempt failed")

                            login_attempts += 1
                    except KeyboardInterrupt: #stopping the script
                        print("\nKeyboard interrupt received. Exiting the script.")
                        log_event("Keyboard interrupt received. Exiting the script.","")

                        exit_script()
            else: 
                print("No login required")
                sleep(1)

            os.system('cls')
            # Specify the path to your text file containing commands
            # file_path = "conf.txt"

            with open(file_path, "r") as file:
                    commands = file.readlines()
                    
            for command in commands:
                    command = command.strip()
                    tn.write(command.encode('ascii') + b'\r')
                    sleep(1)
                    output = tn.read_very_eager().decode('ascii')
                    print(output, end="") 
                    if "--More--" in output:
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
                    if "Invalid input detected" in output:
                        action = input("\n\n" + RED + """Something went wrong :( Do you want to proceed (y/n/e)? 
                                    e : Edit this line \n\n""" + RESET).strip().lower()


                        if action == 'n':
                            exit_script()
                        elif action == 'e':
                            command = input("").strip()
                            tn.write(command.encode('ascii') + b'\r')
                            sleep(1)
                            output = tn.read_very_eager().decode('ascii')
                            print(output, end="") 

                    log_event("Command Executed", f"Input: {command}\nOutput: {output}")
                    
                    


            print(GREEN + "\n\nConfiguration injected successfully"+ RESET)
            log_event("Configuration injected successfully","")
        
                    


    except KeyboardInterrupt:
            sleep(1)
            log_event("KeyboardInterrupt detected, exiting...","")
            exit_script()  # Exit the script gracefully

            sleep(1)
            tn.write(b"exit\r")
            sleep(1)
            tn.write(b"\r")

            tn.close()


if __name__ == '__main__':
    main()