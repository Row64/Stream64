# Send Email Example

from row64tools.email64 import email64

e64 = email64()

# Send email example
e64.send_email("This email was sent by the StreamAPI!")

# Edit subject example
# e64.send_email("GeoFence Alert: id: " + idStr, subject="GeoFence Alert")