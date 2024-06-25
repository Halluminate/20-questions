#!/usr/bin/env python

from twilio.rest import Client

account_sid = 'AC96592646da64a615b1568d84086d9fe5'
auth_token = '9e09c58943d2a92f0bb40312443d995d'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='+18445241860',
  body='Hello from Twilio',
  to='+18475029296'
)

print(message.sid)
