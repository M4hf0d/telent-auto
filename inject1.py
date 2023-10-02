import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QTextEdit, QInputDialog, QCheckBox



import telnetlib
import getpass
from time import sleep
import re
import datetime


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Injector")
        self.setGeometry(100, 100, 400, 500)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # IP Address Input
        ip_label = QLabel("IP Address:")
        self.ip_input = QLineEdit()
        self.ip_input.setInputMask("000.000.0.0;")  # Use setInputMask to enforce the format
        layout.addWidget(ip_label)
        layout.addWidget(self.ip_input)

        # Port Number Input
        port_label = QLabel("Port Number:")
        self.port_input = QLineEdit()
        layout.addWidget(port_label)
        layout.addWidget(self.port_input)


        self.log_checkbox = QCheckBox("Create Log File")
        layout.addWidget(self.log_checkbox)
        # File Upload Button
        self.file_button = QPushButton("Upload Text File")
        layout.addWidget(self.file_button)

        # Label to display the selected file name
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        # Text Output
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)  # Make the text area non-editable
        layout.addWidget(self.text_output)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)

        central_widget.setLayout(layout)

        self.file_button.clicked.connect(self.open_file_dialog)
        self.submit_button.clicked.connect(self.execute)


    
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select File', "Desktop", 'Text Config Files (*.txt)')

        if file_path:
            # Get only the file name without the full path
            file_name = os.path.basename(file_path)
            self.file_label.setText(file_name)

            # Open and read the selected TXT file
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    # Print the lines to the text output widget
                    self.text_output.setPlainText(''.join(lines))
            except Exception as e:
                self.text_output.setPlainText(f"Error reading file: {str(e)}")

    def execute(self):
        tarea=""
        def exit_script(tarea):
                if log: 
                    with open("script_log.txt", "a") as log_file:
                        log_file.write("------------------------------------------------------------\n")
                
                tarea += "\n\n Terminating the script execution. Sending 'exit' and closing the connection...."
                self.text_output.setPlainText(tarea)
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
                
        
        def log_event(event_description, event_details):
                    if log:
                        with open("script_log.txt", "a") as log_file:

                            current_datetime = datetime.datetime.now()
                            timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

                            log_entry = f"[{timestamp}] - {event_description}\n{event_details}\n\n"

                            log_file.write(log_entry)
        
        
        ip = self.ip_input.text()
        port = self.port_input.text()
        file_name = self.file_label.text()
        log = self.log_checkbox.isChecked()


          # Get the selected file name
        try:
            tn = telnetlib.Telnet(ip, port)
        except ConnectionRefusedError:
            print("Connection refused. Check the server address and port.")
            log_event(f"Connecting to Telnet server at {ip} on port {port}." , " \n - Connection refused. Check the server address and port.")

        except Exception as e:
            print(f"An error occurred: {e}")
            log_event(f"Connecting to Telnet server at {ip} on port {port}.", f"\n - An error occurred: {e}")

            sys.exit(1)
        else:
            
            print("Connected to the Telnet server.")
            log_event(f"Connecting to Telnet server at {ip} on port {port}.", f"\n   - Connection successful.")

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
                    # Login
                    user, ok = QInputDialog.getText(self, "Login", "Username:")
                    if ok:
                            password, ok = QInputDialog.getText(self, "Login", "Password:", QLineEdit.EchoMode.Password)
                            if ok:

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

            else: 
                print("No login required")
                self.text_output.setPlainText("No login Required")  # Print the output as it's received

                sleep(1)

            

        with open(file_name, "r") as file:
            commands = file.readlines()
        for command in commands:
                    command = command.strip()
                    tn.write(command.encode('ascii') + b'\r')
                    sleep(1)
                    output = tn.read_very_eager().decode('ascii')
                    tarea += output
                    print(output, end="")
                    self.text_output.setPlainText(tarea)  # Print the output as it's received

                    if "--More--" in output:
                        while True:
                            # Read the output
                            output = tn.read_very_eager().decode('ascii')
                            print(output, end="")
                            tarea += output
                            self.text_output.setPlainText(tarea)  # Print the output as it's received

                            # Check if "--More--" is in the output
                            if "--More--" in output:
                                # Send an Enter keypress to continue
                                tn.write(b"\r")
                                sleep(0.1)  
                            else:
                                break  # Exit the loop when "--More--" is no longer present
                    if "Invalid input detected" in output:
                        pass
                        # action = input("\n\n" + RED + """Something went wrong :( Do you want to proceed (y/n/e)? 
                        #             e : Edit this line \n\n""" + RESET).strip().lower()


                        # if action == 'n':
                        #     exit_script()
                        # elif action == 'e':
                        #     command = input("").strip()
                        #     tn.write(command.encode('ascii') + b'\r')
                        #     sleep(1)
                        #     output = tn.read_very_eager().decode('ascii')
                        #     print(output, end="") 

                    log_event("Command Executed", f"Input: {command}\nOutput: {output}")
                    
                    


            # print(GREEN + "\n\nConfiguration injected successfully"+ RESET)
        log_event("Configuration injected successfully","")
        exit_script(tarea)        
        # Check if login is required
        # login = True  # Set this to your actual condition
        # if login:
        #     user, ok = QInputDialog.getText(self, "Login", "Username:")
        #     if ok:
        #         password, ok = QInputDialog.getText(self, "Login", "Password:", QLineEdit.EchoMode.Password)
        #         if ok:
        #             # Here, you can use the 'user' and 'password' values for authentication
        #             # For example, print them to the text output widget
        #             result = f"IP Address: {ip}\nPort Number: {port}\nFile Name: {file_name}\nUsername: {user}\nPassword: {password}"
        #             self.text_output.setPlainText(result)
        # else:
        #     result = f"IP Address: {ip}\nPort Number: {port}\nFile Name: {file_name}"
        #     self.text_output.setPlainText(result)


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
