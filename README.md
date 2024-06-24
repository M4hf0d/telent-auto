# Injector a Network Configuration Application

In response to the team's requirements, I developed two versions of a network configuration tool: a CLI script and a desktop application using Python and PyQt. Both versions address various needs related to the configuration of network equipment, specifically Cisco devices. Although these are initial iterations, they already demonstrate several essential features to optimize the configuration process.

## Screenshots

![Screenshot 1](https://i.ibb.co/tJ3md2k/Screenshot-1.png)
![Screenshot 2](https://i.ibb.co/PZW3FSK/Screenshot-2.png)
![Screenshot 3](https://i.ibb.co/YR7yPY5/Screenshot-3.png)
![Screenshot 4](https://i.ibb.co/CQpDYPJ/Screenshot-4.png)
![Screenshot 5](https://i.ibb.co/qMxJ6P8/Screenshot-5.png)

## Current Features

### Telnet Server Connection
The application establishes a connection to the router via IP and port using Telnet. This provides a direct interface to interact with devices remotely.

### Configuration Backup and Injection
The application performs a backup of the current configuration before injecting new configuration files. This functionality simplifies updating configuration settings across multiple devices simultaneously.

### Error Management and Rollback
In the event of errors during the configuration injection, the application offers options to resolve the issues. Users can roll back to the previous configuration, undo modifications, or edit specific commands that caused problems.

### Authentication
The application manages the authentication process by requesting the necessary credentials to access the devices, ensuring secure and authorized access.

### Logging
The application generates a log file that records all operations performed, allowing for tracking changes made to the configuration for future reference and troubleshooting.

## Versions

### CLI Script
The CLI version provides all functionalities in a command-line interface, allowing for straightforward and scriptable interactions with network equipment.

### Desktop Application (PyQt)
The desktop application version, built with PyQt, offers a graphical user interface for easier interaction and management of network configurations.

## Future Enhancements

### Vendor Support Expansion
Currently tailored for Cisco equipment, future iterations aim to extend support to other vendors such as Juniper and other brands, enhancing versatility.

### Compliance Check
Future versions will include functionality for verifying configuration compliance with the company's IP addressing plan, ensuring IP addresses and ports conform to established standards.

### Improved User Interface
Plans to enhance the desktop application's user interface will focus on making it more user-friendly and intuitive, improving the overall user experience.

## Summary
Despite being initial iterations, both the CLI script and the desktop application have demonstrated their value by simplifying and improving the Cisco equipment configuration process. With future enhancements, these tools have the potential to become even more powerful and versatile for the entire IP operations department.

---

Feel free to contribute, report issues, or suggest improvements to help make these tools better for everyone involved in network configuration and management.
