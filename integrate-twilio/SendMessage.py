from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "ACa44e0e937603c21239e4c8e2aa1ae3ad"
# Your Auth Token from twilio.com/console
auth_token  = "535bfd711a57d1df2869ed6eb3507265"

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+13474143525", 
    from_="+19293121640",
    body="Hello There!")

print(message.sid)