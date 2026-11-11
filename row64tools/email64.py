import smtplib
import ssl
from getpass import getpass
from email.message import EmailMessage
import os
import json
from cryptography.fernet import Fernet

class email64:

	def __init__(self):

		self.default_sender = ""
		self.default_smtp = "smtp.gmail.com"
		self.default_port = 465
		self.default_path_conf = '/opt/row64server/conf/email_config.json'
		self.default_path_pwd = '/opt/row64server/conf/email_pwd.txt'
		self.default_password = ""
		self.default_path_key = '/opt/row64server/conf/email_key.txt'
		self.default_recipient = ""
		self.default_subject = "Test email from Python"

		self.smtp = self.default_smtp
		self.port = self.default_port
		self.password = self.default_password
		self.path_conf = self.default_path_conf
		self.path_pwd = self.default_path_pwd
		self.path_key = self.default_path_key
		self.email_sender = self.default_sender
		self.email_recipient = self.default_recipient
		self.email_subject = self.default_recipient


	def send_email(self, body, subject=None):

		with open(self.path_conf, "r") as f:
			loaded_config = json.load(f)
			f.close()

		self.email_sender = loaded_config["SENDER_EMAIL"]
		self.smtp = loaded_config["SMTP_SERVER"]
		self.port = int(loaded_config["PORT"])
		self.path_pwd = loaded_config["P_PATH"]
		self.path_key = loaded_config["K_PATH"]
		self.email_recipient = loaded_config["EMAIL_RECIPIENT"]
		self.email_subject = loaded_config["EMAIL_SUBJECT"]

		print("\nGot config from file:\n")
		print("email_sender: " + self.email_sender)
		print("smtp: " + self.smtp)
		print("port: " + str(self.port))
		print("Password file path: " + self.path_pwd)
		print("Key file path: " + self.path_key)
		print("Email recipient: " + self.email_recipient)
		print("Email subject: " + self.email_subject + "\n")

		msg = EmailMessage()
		msg["to"] = self.email_recipient
		if subject != None: msg["subject"] = subject
		else: msg["subject"] = self.email_subject
		msg.set_content(body)

		print("Pending email will use the following values (note that if these values differ than those in the config file, overrides are being applied at the function's call):\n")
		print(f"Recipient: {msg["to"]}")
		print(f"Subject: {msg["subject"]}")
		print(f"Body: {msg.get_content()}\n")

		print("Attempting to get password from file...")
		self.password = self.__get_password()

		print("Attempting to send email...")

		context = ssl.create_default_context()
		with smtplib.SMTP_SSL(
			self.smtp,
			self.port,
			context=context,
			) as server:
			server.login(self.email_sender, self.password)
			server.send_message(msg)


	def setup(self, new_setup=False, new_password=False):

		if new_setup == True:
			print("new_setup set to True. Launching configuration setup...")
			self.__config_setup()

		if new_password == True:
			print("new_password set to True. Launching password setup...")
			self.__password_setup()


		if os.path.isfile(self.path_conf):

			# print("Config file found. Reading values...")
			print("Config file found.")
			with open(self.path_conf, "r") as f:

				# Determine if file is empty
				f.seek(0, os.SEEK_END)
				file_size = f.tell()
				f.seek(0)

				# If file is found but empty, run config setup				
				if file_size == 0:
					print("Config file found, but is empty. Launching setup.")
					self.__config_setup()

				f.close()

		else:

			print("Config file not found. Entering setup...")
			self.__config_setup()

		# Get or set the password
		self.password = self.retrieve_password()

		print("Setup complete")

	# Write the configuration file
	def __write_config(self):
		with open(self.path_conf, "w") as f:
			pending_config = {
				"SENDER_EMAIL": self.email_sender,
				"SMTP_SERVER": self.smtp,
				"PORT": self.port,
				"P_PATH": self.path_pwd,
				"K_PATH": self.path_key,
				"EMAIL_RECIPIENT": self.email_recipient,
				"EMAIL_SUBJECT": self.email_subject,
				# "EMAIL_BODY": self.email_body
			}
			f.write(json.dumps(pending_config))
			f.close()


	def __config_setup(self):

		print("\nPlease enter your configuration options as prompted.\n")

		# Take input
		in_sender = input("Sending email address: ")
		in_smtp = input("SMTP server (e.g. smtp.gmail.com): ")
		in_port = input(f"Port number (i.e. 465 for Gmail or 587 for M365): ")
		in_path_pwd = input(f"Password file path with file name and extension (e.g. ~/Documents/password.txt) (leave blank for default of {self.path_pwd}): ")
		in_path_key = input(f"Key file path with file name and extension (e.g. ~/Documents/key.txt) (leave blank for default of {self.path_key}). It is highly recommended to store this key in a secure location. Please manage responsibly. Enter key file path: ")
		in_email_recipient = input("Email recipient: ")
		in_email_subject = input("Email subject: ")

		if in_port.strip() != "": self.port = int(in_port)
		if in_path_pwd.strip() != "": self.path_pwd = in_path_pwd
		if in_path_key.strip() != "": self.path_key = in_path_key
		self.email_recipient = in_email_recipient
		self.email_subject = in_email_subject
		self.smtp = in_smtp
		self.email_sender = in_sender

		print("\nYour pending configuration:\n")
		print(f"Sending email: {self.email_sender}")
		print(f"SMTP server: {self.smtp}")
		print(f"Port: {str(self.port)}")
		print(f"Password file path: {self.path_pwd}")
		print(f"Key file path: {self.path_key}")
		print(f"Email recipient: {self.email_recipient}")
		print(f"Email subject: {self.email_subject}")
		verify = input("\nIf these values are correct, select ENTER. To redo, input 'r': ")

		match verify:
			case "r":
				self.email_sender = self.default_sender
				self.smtp = self.default_smtp
				self.port = self.default_port
				self.path_pwd = self.default_path_pwd
				self.path_key = self.default_path_key
				self.__config_setup()
			case "":
				print("\nValues accepted. The specified configuration values will be written to the configuration file and used for subsequent script executions.\n")
				self.__write_config()
			case _:
				print("\nUnrecognized input. Exiting setup\n")
				return


	def retrieve_password(self):
		print("Searching for password file: " + self.path_pwd)

		if os.path.exists(self.path_pwd):
			print("Password file found\n")
		else:
			print("File not found\n")
			self.__password_setup()

		return self.__get_password()


	def __prepare_encryption_key(self):

		key = Fernet.generate_key()

		with open(self.path_key, "w") as f:
			f.write(key.decode("utf-8"))


	def __get_key(self):
		f = open(self.path_key, "r")
		keyString = f.read()
		f.close()

		keyString.encode("utf-8")
		return Fernet(keyString)


	def __encrypt_text(self, plaintext):
		key = self.__get_key()
		return key.encrypt(plaintext.encode())


	def __password_setup(self):
		self.__prepare_encryption_key()
		print("Entering app password setup...")
		appPwd = getpass("Enter app password: ", echo_char='*')
		print("\n")

		with open(self.path_pwd, "w") as f:
			f.write(self.__encrypt_text(appPwd).decode())
			f.close()


	def __get_password(self):
		key = self.__get_key()
		with open(self.path_pwd, "r") as f:
			encrypted = f.read()
			f.close()
		encrypted = encrypted.encode("utf-8")
		decrypted = key.decrypt(encrypted)
		decrypted = decrypted.decode("utf-8")
		return decrypted

