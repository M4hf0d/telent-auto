import sys
import os
from PyQt6.QtCore import Qt, QThread, pyqtSignal,pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QTextEdit, QInputDialog, QCheckBox





import telnetlib
import getpass
from time import sleep
import re
import datetime


class TelnetWorker(QThread):
    output_signal = pyqtSignal(str)  # Signal to send Telnet output to the main thread
    close_signal = pyqtSignal()
    
    logininfo_signal = pyqtSignal(str,str)
    login_signal = pyqtSignal()

    def __init__(self, ip, port, commands, log, tn ):
        super().__init__()
        self.ip = ip
        self.port = port
        self.commands = commands
        self.log = log
        self.tarea = ""
        self.tn = tn
        self.username = ""  # Store the username
        self.password = ""  # Store the password

        
        
        self.close_signal.connect(self.close_script)

        self.logininfo_signal.connect(self.logininfo)


    def logininfo(self, user,password):
        self.username = user
        self.password = password


    @pyqtSlot()
    def close_script(self):
            if self.log: 
                with open("script_log.txt", "a") as log_file:
                        log_file.write("------------------------------------------------------------\n")
                
                self.tarea += "\n\n Window Closed, Terminating the script execution. Sending 'exit' and closing the connection...."
                self.output_signal.emit(self.tarea)
                sleep(2)
                ctrl_c = chr(3)  # ASCII code for Ctrl+C
                self.tn.write(ctrl_c.encode('ascii'))
                sleep(1)
                # output = tn.read_very_eager().decode('ascii')
                # print(output, end="")  # Print the output as it's received
                self.tn.write(b"\r")
                sleep(1)
                self.tn.write(b"exit\r")
                sleep(1)
                self.tn.close()



    def run(self):
        tarea =""
        def exit_script():
            if self.log: 
                with open("script_log.txt", "a") as log_file:
                        log_file.write("------------------------------------------------------------\n")
                
                self.tarea += "\n\n Terminating the script execution. Sending 'exit' and closing the connection...."
                self.output_signal.emit(tarea)
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
            if self.log:
                        with open("script_log.txt", "a") as log_file:

                            current_datetime = datetime.datetime.now()
                            timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

                            log_entry = f"[{timestamp}] - {event_description}\n{event_details}\n\n"

                            log_file.write(log_entry)
        
        
        try:
            tn = telnetlib.Telnet(self.ip, self.port)
        except ConnectionRefusedError:
            self.output_signal.emit("Connection refused. Check the server address and port.")
            return
        except Exception as e:
            self.output_signal.emit(f"An error occurred: {e}")
            return

        self.output_signal.emit("Connected to the Telnet server.")

        # ... Rest of your Telnet connection logic ...
        log_event(f"Connecting to Telnet server at {self.ip} on port {self.port}.", f"\n   - Connection successful.")

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
                    self.login_signal.emit()
                    print("sent login signal to main thread")
                    while (not self.username) and ( not self.password):
                             sleep(1)

                    tn.write(self.username.encode('ascii') + b"\r")
                    sleep(1)
                    while not self.password:
                        sleep(1)
                    tn.write(self.password.encode('ascii') + b"\r")
                    sleep(2)

                    output = tn.read_very_eager().decode('ascii')
                    sleep(1)

                    if re.search(r'R\d+#', output): # login successfull "R2#" is in output
                            logged_in = True
                            log_event(f"Loggin as '{self.username}'. ","- Login Successful")

                    else:
                            print("\n\nLogin attempt failed. Please try again.")
                            log_event(f"Loggin as '{self.username}'. ","- Login attempt failed")

                            login_attempts += 1

        else: 
                print("No login required")
                self.output_signal.emit("No login Required")  # Print the output as it's received

                sleep(1)

            
        for command in self.commands:
            command = command.strip()
            tn.write(command.encode('ascii') + b'\r')
            sleep(1)
            output = tn.read_very_eager().decode('ascii')
            self.output_signal.emit(output)  # Emit the output to update the text area in real time

            if "--More--" in output:
                while True:
                    # Read the output
                    output = tn.read_very_eager().decode('ascii')
                    self.output_signal.emit(output)  # Emit the output to update the text area in real time

                    # Check if "--More--" is in the output
                    if "--More--" in output:
                        # Send an Enter keypress to continue
                        tn.write(b"\r")
                        sleep(0.1)
                    else:
                        break  # Exit the loop when "--More--" is no longer present

            if "Invalid input detected" in output:
                self.output_signal.emit("Stopping Script Execution, Please Correct the error and try again.")
                exit_script()
            sleep(1)  # Sleep for 1 second after each command

        
        log_event("Command Executed", f"Input: {command}\nOutput: {output}")
        # log_event("Configuration injected successfully","")
        exit_script()




    


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

        ip_label = QLabel("IP Address:")
        self.ip_input = QLineEdit()
        self.ip_input.setInputMask("000.000.000.000;")  # Use setInputMask to enforce the format
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

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)  # Make the text area non-editable
        layout.addWidget(self.text_output)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)

        central_widget.setLayout(layout)

        self.file_button.clicked.connect(self.open_file_dialog)

        self.submit_button.clicked.connect(self.execute)


        central_widget.setLayout(layout)
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
        ip = self.ip_input.text()
        port = self.port_input.text()
        file_name = self.file_label.text()
        log = self.log_checkbox.isChecked()

        # Get the selected file name and read commands
        try:
                tn = telnetlib.Telnet(ip, port)
        except ConnectionRefusedError:
                self.text_output.append("Connection refused. Check the server address and port.")
                return
        except Exception as e:
                self.text_output.append(f"An error occurred: {e}")
                return

            # Get the selected file name and read commands
        with open(file_name, "r") as file:
                commands = file.readlines()
        # Create and start the TelnetWorker thread
        self.telnet_worker = TelnetWorker(ip, port, commands, log, tn)
        self.telnet_worker.output_signal.connect(self.update_text_output)
        self.telnet_worker.login_signal.connect(self.login)
        # self.telnet_worker.login_cred.connect


        self.telnet_worker.start()

    def login(self):
        print("login signal received")
        user, ok = QInputDialog.getText(self, "Login", "Username:")
        if ok:
            password, ok = QInputDialog.getText(self, "Login", "Password:", QLineEdit.EchoMode.Password)
            if ok:
                self.telnet_worker.logininfo_signal.emit(user, password)
                print("login creds emited")
                 
                 
         
    def update_text_output(self, text):
        # Update the text area with the received text
        self.text_output.append(text)

    
    def closeEvent(self, event):
        # Emit the close_signal to handle closing the application
        self.telnet_worker.close_signal.emit()
        event.accept()



def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
