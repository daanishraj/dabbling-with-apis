
"""Integrate our app with the SendGrid API so we can send an email to user"""

from flask import Flask
#from flask_restful import Resource, Api
from flask import jsonify
from flask import request
import ssl

app = Flask(__name__)
#api = Api(app)


#############using mail helper class***************************************
# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import sendgrid
import os
from sendgrid.helpers.mail import *
import os
from sendgrid.helpers.mail import *



ssl._create_default_https_context = ssl._create_unverified_context

@app.route('/sendmail', methods=['POST'])
def post():
	sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
	sender_email=request.json['sender_email']
	receiver_email=request.json['receiver_email']
	subject_matter=request.json['subject']
	content_email=request.json['content']
	mail = Mail(Email(sender_email), subject_matter, Email(receiver_email), Content("text/plain", content_email))
	response = sg.client.mail.send.post(request_body=mail.get())
	print(response.status_code)
	print(response.body)
	print(response.headers)
	return jsonify(status = 'OK',message = 'email sent successfully')






# #############without  mail helper class***************************************
# import sendgrid
# import os
# try:
#     # Python 3
#     import urllib.request as urllib
# except ImportError:
#     # Python 2
#     import urllib2 as urllib

# sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
# data = {
#   "personalizations": [
#     {
#       "to": [
#         {
#           "email": "test@example.com"
#         }
#       ],
#       "substitutions": {
#         "-name-": "Example User",
#         "-city-": "Denver"
#       },
#       "subject": "I'm replacing the subject tag"
#     },
#   ],
#   "from": {
#     "email": "test@example.com"
#   },
#   "content": [
#     {
#       "type": "text/html",
#       "value": "I'm replacing the <strong>body tag</strong>"
#     }
#   ],
#   "template_id": "13b8f94f-bcae-4ec6-b752-70d6cb59f932"
# }
# try:
#     response = sg.client.mail.send.post(request_body=data)
# except urllib.HTTPError as e:
#     print (e.read())
#     exit()
# print(response.status_code)
# print(response.body)
# print(response.headers)

if __name__ == '__main__':
	app.run(debug=True)




