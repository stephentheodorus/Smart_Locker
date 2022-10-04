import smtplib
from email.message import EmailMessage

from kink import inject


class SendEmail:
    def send_email_to_new_user(self, id, name, email):
        pass

    def notify_new_package(
        self, email, name, locker_id, item_type, item_size, verification
    ):
        pass

    def retrieve_package_reminder(self, name, email):
        pass

    def notify_operator_five_times_wrong_id_input(self):
        pass


@inject
class Emailer(SendEmail):
    def __init__(self, email, password):
        self.email = email
        self.password = password

    ### Send email to new user
    def send_email_to_new_user(self, id, name, email):
        html = f"""\
        <!DOCTYPE html>
        <html>
          <body>
            <p> Welcome, {name}! Thank you for registering as a new user for SchliessFach locker service. <br>
                Your id is <b>{id}</b>. <br>
                We hope you enjoy our service. <br>
                <br>
                <br>
                Sincerely, <br>
                <br>
                <b>SchliessFach Administrator.</b>
            </p>
          </body>
        </html>
        """

        msg = EmailMessage()
        msg["Subject"] = "Welcome to SchliessFach!"
        msg["From"] = self.email
        msg["To"] = email

        # msg.set_content(msg_body)
        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)

    # END#

    ### Notify new package to user
    def notify_new_package(
        self, email, name, locker_id, item_type, item_size, verification
    ):
        html = f"""\
        <!DOCTYPE html>
        <html>
          <body>
            <p> Hello, {name}. A new package has just come for you. <br>
                <br>
                Item type: {item_type} <br>
                Item size: {item_size} <br>
                <br>
                The package is stored in locker number <b>{locker_id}</b>. <br>
                Your verification code is: <b>{verification}</b> <br>
                Please collect your package as soon as possible.<br>
                <br>
                <br>
                Sincerely, <br>
                <br>
                <b>SchliessFach Administrator.</b>
            </p>
          </body>
        </html>
        """

        msg = EmailMessage()
        msg["Subject"] = "You Got A Package!"
        msg["From"] = self.email
        msg["To"] = email

        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)

    # END#

    def retrieve_package_reminder(self, name, email):
        html = f"""\
                <!DOCTYPE html>
                <html>
                  <body>
                    <p> Hello {name}. <br>
                    Please retrieve your package as soon as possible, because there is currently only one empty locker left available. <br>
                    <br>
                    <br>
                    Sincerely, <br>
                    
                    <b>SchliessFach Administrator</b>
                    </p>
                  </body>
                </html>
                """

        msg = EmailMessage()
        msg["Subject"] = "Reminder to Retrieve Your Package"
        msg["From"] = self.email
        msg["To"] = email

        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)

    def notify_operator_five_times_wrong_id_input(self):
        html = f"""\
        <!DOCTYPE html>
        <html>
          <body>
            <p> Dear operator, <br>
            The system has detected invalid id inputs for five consecutive times. Please kindly check or contact security.
            </p>
          </body>
        </html>
        """

        msg = EmailMessage()
        msg["Subject"] = "Warning! Five Times Wrong Inputted ID."
        msg["From"] = self.email
        msg["To"] = self.email

        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)


class MockEmailer(SendEmail):
    def __init__(self):
        pass

    def send_email_to_new_user(self, id, name, email):
        return True

    def notify_new_package(
        self, email, name, locker_id, item_type, item_size, verification
    ):
        return True

    def retrieve_package_reminder(self, name, email):
        return True

    def notify_operator_five_times_wrong_id_input(self):
        return True
