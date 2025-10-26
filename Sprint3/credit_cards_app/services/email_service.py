import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


class GmailEmailClient:
	def __init__(self):
		self.username = os.environ.get("GMAIL_USER")   # tu cuenta Gmail
		self.password = os.environ.get("GMAIL_PASS")   # contraseña de aplicación
		self.host = "smtp.gmail.com"
		self.port = 587

	def send(self, to_email: str, subject: str, html_body: str, text_body: str = None):
		text_body = text_body or "Notificación de tu cuenta."
		msg = MIMEText(html_body, "html", "utf-8")
		msg["Subject"] = subject
		msg["From"] = formataddr(("Soporte", self.username))
		msg["To"] = to_email

		with smtplib.SMTP(self.host, self.port) as server:
			server.starttls()
			server.login(self.username, self.password)
			server.sendmail(self.username, [to_email], msg.as_string())
