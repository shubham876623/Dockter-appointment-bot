import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()


class TwilioService:
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    @classmethod
    def send_whatsapp(cls, to, message):

        cls.client.messages.create(
            from_=cls.TWILIO_WHATSAPP_NUMBER,
           
            body=message,
            to=f'whatsapp:{to}'
        )

    @classmethod
    def send_sms(cls, to, message):
        print(to)
        cls.client.messages.create(
            from_='+14847896028',
            body=message,
            to=to
        )
