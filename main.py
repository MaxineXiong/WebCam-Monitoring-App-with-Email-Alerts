import cv2
import time
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication



class WebCam:
    DURATION_THRESHOLD = 5 * 60

    def __init__(self, camera_index=0):
        self.video = cv2.VideoCapture(camera_index)
        self.first_frame = None
        self.statuses = []
        self.entry_time = None
        self.alert_email_sent = False


    def send_email(self, in_camera: bool, attachment_filename: str):
        incident_id = 'incident-' + self.entry_time.strftime('%Y%m%d-%H%M%S')
        entry_time_str = self.entry_time.strftime('%b %d, %Y, at %I:%M:%S %p')
        if in_camera:
            duration_threshold_mins = round(self.DURATION_THRESHOLD/60, 2)
            # Define the email subject line for the alert email
            subject = f'Security Alert {incident_id}: Unusual Prolonged Presence Detected'
            # Read the content from the template for alert emails
            with open('./email-body-templates/alert-email-html-body.txt', 'r') as file:
                body = file.read()
            # Format the email template string to construct the HTML body of the alert email
            body = body%(entry_time_str, duration_threshold_mins, incident_id,
                         entry_time_str, duration_threshold_mins)
        else:
            exit_time = datetime.now()
            exit_time_str = exit_time.strftime('%b %d, %Y, at %I:%M:%S %p')
            # Define the email subject line for the update email
            subject = f'Security Update on {incident_id}: Detected Individual Has Left the Monitored Area'
            # Read the content from the template for update emails
            with open('./email-body-templates/update-email-html-body.txt', 'r') as file:
                body = file.read()
            # Format the email template string to construct the HTML body of the update email
            body = body%(incident_id, entry_time_str, exit_time_str,
                         round((exit_time - self.entry_time).seconds/60, 2))
        # Set up Email account credentials and SMTP server details
        sender_email = "meenoxiong@gmail.com"
        recipient_email = "meeno2b@outlook.com"
        # To generate an app password for this program, go to ...
        # ...https://myaccount.google.com/security, search "App Passwords", ...
        # ...and create one
        sender_password = "gclcitlssbmcavmf"
        smtp_server = 'smtp.gmail.com'
        smtp_port = 465    # Port number for SSL
        path_to_attachment = attachment_filename

        # Create a MIMEMultipart object to combine different parts of the email
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        # Attach the HTML body part to the email
        body_part = MIMEText(body, 'html')
        message.attach(body_part)

        # Check if the file name of attachment is provided
        if attachment_filename:
            # If so, attach the file to the email
            with open(path_to_attachment, 'rb') as file:
                message.attach(MIMEApplication(file.read(), Name=attachment_filename))

        # Login to the SMTP server and send the email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
           server.login(sender_email, sender_password)
           server.sendmail(sender_email, recipient_email, message.as_string())

        # Print a confirmation message after sending an email
        if in_camera:
            print(f'An alert email containing a captured image of the detected object has been sent to {recipient_email}.')
        else:
            print('An update email has been sent to notify that the detected individual has left the monitored area.')


    def monitor(self):
        time.sleep(2)

        while True:
            status = 0

            _, frame = self.video.read()

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            if self.first_frame is None:
                self.first_frame = gray_frame_gau
                self.statuses.append(status)
                continue

            delta_frame = cv2.absdiff(self.first_frame, gray_frame_gau)

            thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]

            dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

            contours, _ = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) >= 5000:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    status = 1

            cv2.imshow('frame with rectangles', frame)

            key = cv2.waitKey(1)

            if key == ord('q'):
                break

            if (status == 1) and (self.statuses[-1] == 0):
                self.entry_time = datetime.now()
            if (status == 0) and (self.statuses[-1] == 1):
                if self.alert_email_sent:
                    self.send_email(in_camera=False,
                                    attachment_filename=None)
                    self.alert_email_sent = False
                    self.entry_time = None

            if self.entry_time:
                current_time = datetime.now()
                duration_sec = (current_time - self.entry_time).seconds

                if duration_sec >= self.DURATION_THRESHOLD:
                    if not self.alert_email_sent:
                        file_name = 'detected_object_{}.jpg'.format(current_time.strftime('%Y%m%d%H%M%S'))
                        cv2.imwrite(file_name, frame)
                        self.send_email(in_camera=True,
                                        attachment_filename=file_name)
                        self.alert_email_sent = True

            self.statuses.append(status)



if __name__ == '__main__':
    camera = WebCam(camera_index=0)
    camera.monitor()
