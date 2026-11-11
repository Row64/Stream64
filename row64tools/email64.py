import smtplib
import ssl
from getpass import getpass
from email.message import EmailMessage
import os
import json
from cryptography.fernet import Fernet

class email64:

	def __init__(self):

		# Default configuration values
		self.default_sender_email = ""
		self.default_smtp_server = ""
		self.default_port = 465
		self.default_config_file_path = '/opt/row64server/conf/r64_send_email_config.json'
		self.default_password_file_path = '/opt/row64server/conf/r64_send_email_eml_pwd.txt'
		self.default_password = ""
		self.default_key_file_path = '/opt/row64server/conf/r64_send_email_key.txt'
		self.default_recipient = ""
		self.default_subject = "Test email from Python"
		self.default_body = "This email was sent by Python."

		# Config values initially set to default values
		self.smtp_server = self.default_smtp_server
		self.port = self.default_port
		self.password = self.default_password
		self.config_file_path = self.default_config_file_path
		self.password_file_path = self.default_password_file_path
		self.key_file_path = self.default_key_file_path
		self.email_sender = self.default_sender_email
		self.email_recipient = self.default_recipient
		self.email_subject = self.default_recipient
		self.email_body = self.default_body


	# ------------------------------------------------
	# EMAIL FUNCTION

	# Send an email based on an existing configuration
	def send_email(self, override_recipient=None, override_subject=None, override_body=None):

		# Build email message and apply overrides, if present
		msg = EmailMessage()
		if override_recipient != None: msg["to"] = override_recipient
		else: msg["to"] = self.email_recipient
		if override_subject != None: msg["subject"] = override_subject
		else: msg["subject"] = self.email_subject
		if override_body != None: msg.set_content(override_body)
		else: msg.set_content(self.email_body)

		print("Pending email will use the following values (note that if these values differ than those in the config file, overrides are being applied at the function's call):\n")
		print(f"Recipient: {msg["to"]}")
		print(f"Subject: {msg["subject"]}")
		print(f"Body: {msg.get_content()}\n")

		print("Attempting to send email...\n")

		context = ssl.create_default_context()
		with smtplib.SMTP_SSL(
			self.smtp_server,
			self.port,
			context=context,
			) as server:
			server.login(self.email_sender, self.password)
			server.send_message(msg)


	# ------------------------------------------------
	# CONFIG FUNCTIONS

	# This is the primary config setup function
	# This is the only function that needs to be called to complete a full setup
	def setup(self, new_setup=False, new_password=False):


		if new_setup == True:
			print("new_setup set to True. Launching configuration setup...")
			self.__config_setup()

		if new_password == True:
			print("new_password set to True. Launching password setup...")
			self.__password_setup()


		if os.path.isfile(self.config_file_path):

			print("Config file found. Reading values...")
			with open(self.config_file_path, "r") as f:

				# Determine if file is empty
				f.seek(0, os.SEEK_END)
				file_size = f.tell()
				f.seek(0)

				# If file is found but empty, run config setup				
				if file_size == 0:
					print("Config file found, but is empty. Launching setup.")
					self.__config_setup()

				# Load values
				loaded_config = json.load(f)
				f.close()
			
			# Assign config file values to variables
			self.email_sender = loaded_config["SENDER_EMAIL"]
			self.smtp_server = loaded_config["SMTP_SERVER"]
			self.port = int(loaded_config["PORT"])
			self.password_file_path = loaded_config["P_PATH"]
			self.key_file_path = loaded_config["K_PATH"]
			self.email_recipient = loaded_config["EMAIL_RECIPIENT"]
			self.email_subject = loaded_config["EMAIL_SUBJECT"]
			self.email_body = loaded_config["EMAIL_BODY"]

			# TESTING
			print("\nGot config from file:\n")
			print("email_sender: " + self.email_sender)
			print("smtp_server: " + self.smtp_server)
			print("port: " + str(self.port))
			print("Password file path: " + self.password_file_path)
			print("Key file path: " + self.key_file_path)
			print("Email recipient: " + self.email_recipient)
			print("Email subject: " + self.email_subject)
			print("Email body: " + self.email_body + "\n")

		else:

			print("Config file not found. Entering setup...")
			self.__config_setup()

		# Get or set the password
		self.password = self.retrieve_password()

	# Write the configuration file
	def __write_config(self):
		with open(self.config_file_path, "w") as f:
			pending_config = {
				"SENDER_EMAIL": self.email_sender,
				"SMTP_SERVER": self.smtp_server,
				"PORT": self.port,
				"P_PATH": self.password_file_path,
				"K_PATH": self.key_file_path,
				"EMAIL_RECIPIENT": self.email_recipient,
				"EMAIL_SUBJECT": self.email_subject,
				"EMAIL_BODY": self.email_body
			}
			f.write(json.dumps(pending_config))
			f.close()


	# Retrieve the needed configuration variables from the terminal
	def __config_setup(self):

		print("\nPlease enter your configuration options as prompted.\n")

		# Take input
		in_sender_email = input("Sending email address: ")
		in_smtp_server = input("SMTP server (e.g. smtp.gmail.com): ")
		in_port = input(f"Port number (leave blank for default of {self.port}): ")
		in_password_file_path = input(f"Password file path with file name and extension (e.g. ~/Documents/password.txt) (leave blank for default of {self.password_file_path}): ")
		in_key_file_path = input(f"Key file path with file name and extension (e.g. ~/Documents/key.txt) (leave blank for default of {self.key_file_path}). It is highly recommended to store this key in a secure location. Please manage responsibly. Enter key file path: ")
		in_email_recipient = input("Email recipient: ")
		in_email_subject = input("Email subject: ")
		in_email_body = input("Email body: ")

		# Assign variables
		if in_port.strip() != "": self.port = int(in_port)
		if in_password_file_path.strip() != "": self.password_file_path = in_password_file_path
		if in_key_file_path.strip() != "": self.key_file_path = in_key_file_path
		self.email_recipient = in_email_recipient
		self.email_subject = in_email_subject
		self.email_body = in_email_body
		self.smtp_server = in_smtp_server
		self.email_sender = in_sender_email

		# Confirm inputs
		print("\nYour pending configuration:\n")
		print(f"Sending email: {self.email_sender}")
		print(f"SMTP server: {self.smtp_server}")
		print(f"Port: {str(self.port)}")
		print(f"Password file path: {self.password_file_path}")
		print(f"Key file path: {self.key_file_path}")
		print(f"Email recipient: {self.email_recipient}")
		print(f"Email subject: {self.email_subject}")
		print(f"Email body: {self.email_body}")
		verify = input("\nIf these values are correct, select ENTER. To redo, input 'r': ")

		match verify:
			case "r":
				self.email_sender = self.default_sender_email
				self.smtp_server = self.default_smtp_server
				self.port = self.default_port
				self.password_file_path = self.default_password_file_path
				self.key_file_path = self.default_key_file_path
				#self.config_file_path = self.default_config_file_path
				self.__config_setup()
			case "":
				print("\nValues accepted. The specified configuration values will be written to the configuration file and used for subsequent script executions.\n")
				self.__write_config()
			case _:
				print("\nUnrecognized input. Exiting setup\n")
				return


	# ------------------------------------------------
	# PASSWORD MANAGEMENT FUNCTIONS


	# Primary password retrieval function
	def retrieve_password(self):
		print("Searching for password file: " + self.password_file_path)

		# Enter password setup if no file is found
		if os.path.exists(self.password_file_path):
			print("Password file found\n")
		else:
			print("File not found\n")
			self.__password_setup()

		return self.__get_password()


	# Function that generates an encryption key and stores it in a file
	def __prepare_encryption_key(self):

		# Generate encryption key
		key = Fernet.generate_key()

		# Store the key value in the key file
		# Must be decoded for storage, and must be re-encoded for retrieval
		with open(self.key_file_path, "w") as f:
			f.write(key.decode("utf-8"))


	# Retrieve encryption key from file
	def __get_key(self):
		f = open(self.key_file_path, "r")
		keyString = f.read()
		f.close()

		keyString.encode("utf-8")
		return Fernet(keyString)


	# Function that encrypts text using the key generated in prepare_encryption_key()
	def __encrypt_text(self, plaintext):

		# Get encryption key
		key = self.__get_key()

		# Encrypt
		return key.encrypt(plaintext.encode())


	# Encrypt and store password
	def __password_setup(self):

		self.__prepare_encryption_key()
		print("Entering app password setup...")
		appPwd = getpass("Enter app password: ", echo_char='*')

		print("\n")

		# Create or open password file and overwrite contents
		with open(self.password_file_path, "w") as f:
			f.write(self.__encrypt_text(appPwd).decode())
			f.close()


	# Retrive and decrypt password
	def __get_password(self):

		# Retrieve Fernet key
		key = self.__get_key()

		# Get encrypted password
		with open(self.password_file_path, "r") as f:
			encrypted = f.read()
			f.close()

		# Must encode as bytes before it can be decrypted
		encrypted = encrypted.encode("utf-8")

		# Decrypt
		decrypted = key.decrypt(encrypted)
		decrypted = decrypted.decode("utf-8")

		return decrypted


	# ------------------------------------------------


