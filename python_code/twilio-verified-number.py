# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["ACafb4c3e0b611e9b7c209a99fdac2f235"]
auth_token = os.environ["e47a742920fc8ba7a4363dc4580a03ba"]  # Remplacez par votre Auth Token réel
client = Client(account_sid, auth_token)

validation_request = client.validation_requests \
                           .create(
                                friendly_name='Badr',
                                phone_number='+33764769658'
                            )

print(validation_request.friendly_name)