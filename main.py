import cv2
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import glob
from threading import Thread



class WebCam:
    """Class to monitor a specified area using a webcam and to send
    email alerts based on detected movement within that area.
    """

    # Duration threshold (2-minute) in SECONDS for staying in the camera view
    DURATION_THRESHOLD = 5

    def __init__(self, camera_index: int = 0):
        """Method to initialise an instance of the WebCam class. It sets
        up the webcam device for capturing video and initializes various
        attribute variables used for monitoring and motion detection within
        the specified area.
        Arguments:
        - camera_index (int): The index of the camera device to be used for
        video capture. The default value, 0, typically refers to the built-in
        webcam on a laptop or the first external webcam detected.
        """
        # Initialize the video capture on the specified camera index
        self.video = cv2.VideoCapture(camera_index)
        # Initialize first_frame to None, to be set on first loop of ...
        # ...video capture
        self.first_frame = None
        # Initialize an empty list to track changes in motion detection ...
        # ...status
        self.status_list = []
        # Initialize entry_time to None, to be set and updated when ...
        # ...motion is first detected
        self.entry_time = None
        # Set the initial state of the email alert flag to False
        self.alert_email_sent = False


    def send_email(
            self, entry_time: datetime, in_camera: bool,
            attachment_filename: str):
        """Method to compose and send an email notification based on the
        motion detection status within the monitored area.
        Args:
        - entry_time (datetime): The timestamp when the motion was
        first detected.
        - in_camera (bool): A flag indicating whether the object is in the
        camera view or has left.
        - attachment_filename (str): The file path of the image captured
        during the detection, used as an email attachment.
        """
        # Generate a unique incident ID based on the entry time
        incident_id = "incident-" + entry_time.strftime("%Y%m%d-%H%M%S")
        # Format the entry time to string
        entry_time_str = entry_time.strftime("%b %d, %Y, at %I:%M:%S %p")

        # Check if the detected object is in the camera view
        if in_camera:
            # Calculate the duration threshold in minutes
            duration_threshold_mins = round(self.DURATION_THRESHOLD / 60)
            # Define the email subject line for the security alert email
            subject = (
                f"Security Alert {incident_id}: Unusual Prolonged "
                "Presence Detected"
            )
            # Read the content from the template for alert emails
            with open(
                "./email-body-templates/alert-email-html-body.txt", "r"
            ) as file:
                body = file.read()
            # Format the email template string to construct the HTML body ...
            # ...of the alert email
            body = body%(
                entry_time_str,
                duration_threshold_mins,
                incident_id,
                entry_time_str,
                duration_threshold_mins,
            )
        else:
            # Capture the current time as the exit time
            exit_time = datetime.now()
            # Format the exit time to string
            exit_time_str = exit_time.strftime("%b %d, %Y, at %I:%M:%S %p")
            # Define the email subject line for the security update email
            subject = (
                f"Security Update on {incident_id}: Detected Individual Has "
                "Left the Monitored Area"
            )
            # Read the content from the template for update emails
            with open(
                "./email-body-templates/update-email-html-body.txt", "r"
            ) as file:
                body = file.read()
            # Format the email template string to construct the HTML body ...
            # ...of the update email
            body = body%(
                incident_id,
                entry_time_str,
                exit_time_str,
                round((exit_time - entry_time).seconds / 60),
            )
        # Set up Email account credentials and SMTP server details
        sender_email = "[SENDER-EMAIL-ADDRESS]"
        recipient_email = "[RECIPIENT-EMAIL-ADDRESS]"
        # To generate an app password for this program, go to ...
        # ...https://myaccount.google.com/security, search ...
        # ..."App Passwords", and create one
        sender_password = "[YOUR-APP-PASSWORD]"
        smtp_server = "smtp.gmail.com"
        # Port number for SSL
        smtp_port = 465
        path_to_attachment = attachment_filename

        # Create a MIMEMultipart object to combine different parts ...
        # ...of the email
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        # Attach the HTML body part to the email
        body_part = MIMEText(body, "html")
        message.attach(body_part)

        # Check if the file name of attachment is provided
        if attachment_filename:
            # If so, attach the file to the email
            with open(path_to_attachment, "rb") as file:
                message.attach(
                    MIMEApplication(file.read(),
                                    Name=attachment_filename)
                )

        # Login to the SMTP server and send the email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email,
                            recipient_email,
                            message.as_string())

        # Print a console message confirming the email has been sent
        if in_camera:
            print(
                f"{incident_id}: An alert email containing a captured image "
                f"of the detected object has been sent to {recipient_email}."
            )
        else:
            print(
                f"{incident_id}: An update email has been sent to notify "
                "that the detected individual has left the monitored area."
            )


    def clean_folder(self):
        """Method to clean up any temporary JPEG image files that were saved
        during the monitoring and alerting process.
        """
        # Find all JPEG files in the current directory
        for image in glob.glob("*.jpg"):
            # Delete each temporary image
            os.remove(image)


    def execute_concurrently_in_background(
            self, target_process,
            process_args: tuple = ()):
        """Execute a given process concurrently in a background thread
        Args:
        - target_process (function): The function to be executed in the
        background.
        - process_args (tuple, optional): Arguments to pass to the
        target_process function.
        """
        # Create a new thread to run the given function with its arguments
        thread = Thread(target=target_process, args=process_args)
        # Set the given function to be executed in the background
        thread.daemon = True
        # Start to execute the function concurrently in the background
        thread.start()


    def monitor(self):
        """
        Continuously monitors the webcam feed to detect significant motion
        and manage alerts.
        This method captures frames from the webcam, processes them to detect
        motion in real-time, and takes action based on the presence or
        absence of significant motion. Actions include capturing images,
        sending alert emails, and managing internal state related to motion
        detection.
        """
        # Start an infinite loop for continuous monitoring
        while True:
            # Initiate the detection status variable with 0 indicating ...
            # ...no motion detected initially
            status = 0

            # Read the current frame from the video capture
            _, frame = self.video.read()
            # Convert the current frame to grayscale to simplify the ...
            # ...image processing
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian Blur to smooth the current frame, reducing ...
            # ...detail and noise
            gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            # Initialize the first frame to be used as a baseline for ...
            # ...motion detection
            if self.first_frame is None:
                self.first_frame = gray_frame_gau
                # Append initial status to the status_list
                self.status_list.append(status)
                # Skip to process the next frame directly
                continue

            # Calculate the absolute difference between the current frame ...
            # ...and the first frame
            delta_frame = cv2.absdiff(self.first_frame, gray_frame_gau)
            # Apply a threshold to the delta frame to raise the array value ...
            # ...that is higher than 60 to 255. The resulted frame should ...
            # ...only consist of either 0 (black) or 255 (white)
            thresh_frame = cv2.threshold(delta_frame, 60, 255,
                                         cv2.THRESH_BINARY)[1]
            # Dilate the thresholded frame to fill in holes, making ...
            # ...contours more detectable
            dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
            # Find contours in the dilated frame which represent ...
            # ...boundaries of moving objects
            contours, _ = cv2.findContours(
                dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            # Iterate through each found contour
            for contour in contours:
                # Check the area of the contour to determine whether ...
                # ...it's a target object
                if cv2.contourArea(contour) >= 5000:
                    # If so, compute the attributes of the bounding ...
                    # ...box of the contour, including (x, y) of the ...
                    # ...top left corner, and width and height of the ...
                    # ...bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    # Draw a rectangle on the current original frame ...
                    # ...based on the bounding box attributes
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 3)
                    # Set status to 1 to indicate motion detected
                    status = 1

            # Check if there is a transition from no motion to motion detected
            if (status == 1) and (self.status_list[-1] == 0):
                # Record the current time as the entry time when motion is ...
                # ...first detected
                self.entry_time = datetime.now()
            # Check if there is a transition from motion detected to no motion
            if (status == 0) and (self.status_list[-1] == 1):
                # Check if an alert email has already been sent for the ...
                # ...detected motion
                if self.alert_email_sent:
                    # Execute the send_email method concurrently in the ...
                    # ...background to send a security update email that ...
                    # ...notifies the object has left the monitored area
                    self.execute_concurrently_in_background(
                        target_process=self.send_email,
                        process_args=(self.entry_time, False, None),
                    )
                    # Reset the alert-email-sent flag back to False
                    self.alert_email_sent = False
                    # Reset the entry time back to None
                    self.entry_time = None

            # Check if an object has been detected to enter the monitored area
            if self.entry_time is not None:
                # Capture the current time
                current_time = datetime.now()
                # Calculate the duration in seconds since the motion ...
                # ...was first detected
                duration_sec = (current_time - self.entry_time).seconds
                # Compare the duration against the predefined threshold ...
                # ...to determine if it is an extended presence
                if duration_sec >= self.DURATION_THRESHOLD:
                    # If so, check if an alert email has not already been ...
                    # ...sent for this presence
                    if not self.alert_email_sent:
                        # Generate a filename for saving an image of the ...
                        # ...detected object using the current timestamp
                        file_name = "detected_object_{}.jpg".format(
                            current_time.strftime("%Y%m%d%H%M%S")
                        )
                        # Save the current frame as a JPEG file
                        cv2.imwrite(file_name, frame)
                        # Execute the send_email method concurrently in ...
                        # ...the background to send a security alert email ...
                        # ...that notifies users of the extended presence
                        self.execute_concurrently_in_background(
                            target_process=self.send_email,
                            process_args=(self.entry_time, True, file_name),
                        )
                        # Set the alert-email-sent flag to True to prevent ...
                        # ...sending duplicate alert emails
                        self.alert_email_sent = True

            # Append the current status to the status list
            self.status_list.append(status)

            # Display the frame with detected motion rectangles
            cv2.imshow("Monitoring video with rectangles", frame)

            # Wait for a key press for interruption
            key = cv2.waitKey(1)
            # If 'q' is pressed, break the loop
            if key == ord("q"):
                break

        # Release the video capture device
        self.video.release()

        # Clean up stored temporary images to free space
        self.clean_folder()



# Check if this script is being run directly (and not imported as a module)
if __name__ == "__main__":
    # Initialize the WebCam object
    camera = WebCam(camera_index=0)
    # Start the monitoring process
    camera.monitor()
