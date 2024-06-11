# WebCam Monitoring App with Email Alerts

[![GitHub](https://badgen.net/badge/icon/GitHub?icon=github&color=black&label)](https://github.com/MaxineXiong)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Python](https://img.shields.io/badge/Python->=3.6-blue?logo=python&logoColor=white)](https://www.python.org)

<br>

## Project Description

The **WebCam Monitoring App with Email Alerts** is designed to enhance security by monitoring specific areas and detecting unauthorized or prolonged presence. This application utilizes webcam technology to continuously monitor a designated area, alerting users via email when any object enters and remains in the area beyond a specified duration (default is 2 minutes). This application is ideal for settings that require vigilant security measures such as front and back yards of residential houses, doorway of retail shops, or any sensitive areas needing close monitoring.

<br>

## Features

- **Real-time Monitoring**: Utilizes webcam technology to monitor designated areas in real time.
- **Motion Detection**: Detects and records motion within the monitored area.
- **Automated Email Alerts**: Sends a security alert email if an object remains in the area longer than the specified duration, and a follow-up security update email once the object leaves.
- **Customizable Alert Thresholds**: Users can set the duration threshold that triggers the alert.
- **Versatile Application**: Suitable for residential, commercial, and sensitive environments.

<br>

## Repository Structure

```
WebCamMonitoringApp/
├── main.py
├── email-body-templates/
│   ├── alert-email-html-body.txt
│   └── update-email-html-body.txt
├── sample-output/
│   ├── Security Alert incident-20240611-140712_ Unusual Prolonged Presence Detected.eml
│   └── Security Update on incident-20240611-140712_ Detected Individual Has Left the Monitored Area.eml
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE
```

- **main.py**: This file is the core script containing the Python code for monitoring, motion detection, email alerting, and frame processing functionalities.
- **email-body-templates/**: This directory contains HTML templates for the emails sent by the application. These templates include placeholders (i.e. %s) that are dynamically filled with specific details such as the incident time and duration.
    - **alert-email-html-body.txt**: Serves as the body template for the alert email sent when prolonged presence is detected.
    - **update-email-html-body.txt**: Used for the body of the update email when a detected object leaves the monitored area.
- **sample-output/**: This folder showcases email examples of the output from the application, demonstrating the email alerting functionality. It includes an example of security alert email, and one of follow-up security update email.
- **requirements.txt**: Lists all necessary Python libraries and dependencies required to run the application. These can be installed via the command `pip install -r requirements.txt`.
- **.gitignore**: Specifies which files and directories Git should ignore, helping to keep the repository clean from unnecessary or sensitive files.
- **README.md**: Provides a detailed overview of the repository, including descriptions of its functionality, usage instructions, and information on how to contribute.
- **LICENSE**: The license file for the project.

<br>

## **Usage**

To run the WebCam Monitoring program on your local computer, please follow these steps:

1. Clone this repository to your local machine using the following command:
    
    ```
    git clone https://github.com/MaxineXiong/WebCam-Monitoring-App-with-Email-Alerts.git
    ```
    
2. Download and install the latest version of [Python](https://www.python.org/downloads/) for your system. Make sure to select the "Add Python to PATH" option during the installation process.
3. Navigate to the project folder using File Explorer, type `cmd` in the address bar at the top of the window, and press Enter. This will open Command Prompt in the project folder.
4. Install the required packages by executing the following command in the Command Prompt:
    
    ```
    pip install -r requirements.txt
    ```
    
5. **Configure email settings**: Open `main.py` and update the `sender_email`, `recipient_email`, and `sender_password` variables with your own email credentials and app password.
6. Now launch the WebCam Monitoring program by entering the following command in the Command Prompt:
    
    ```
    python main.py
    ```

<br>

## Contribution

Contributions to improve the WebCam Monitoring App are welcome. Please fork the repository, make your changes, and submit a pull request. We appreciate your input in making this tool more effective and versatile.

<br>

## **License**

This project is licensed under the MIT License. See the [LICENSE](https://choosealicense.com/licenses/mit/) file for more details.

<br>

## Acknowledgements

- [**OpenCV**](https://opencv.org/): For providing the computer vision tools necessary for motion detection.
- [**Python Standard Library**](https://www.python.org/): For supporting system operations and email functionalities.
