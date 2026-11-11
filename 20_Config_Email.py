from row64tools.email64 import email64

# Email config is set up in /opt/row64server/conf/email_config.json
# This file can be edited manually or through python

# Initiate the process to fill out the config from the command prompt
e64 = email64()
e64.setup()

# Trigger new setup processes example
#e64.setup(new_setup = True, new_password = True)
