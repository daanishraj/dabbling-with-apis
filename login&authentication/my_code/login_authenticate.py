import os
from flask import Flask
from flask import Flask, abort, request, jsonify, g, url_for, make_response
from flask_restful import Resource, Api
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson import ObjectId
from requests import put, get
from flask_restful import reqparse
import unittest
from pymongo import MongoClient
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
						  as Serializer, BadSignature, SignatureExpired)
from flask.json import JSONEncoder
from bson import json_util
from flask_login import login_user, logout_user, login_required, \
	current_user 
from flask import flash    
import ssl
import sendgrid
from sendgrid.helpers.mail import *
import os
from sendgrid.helpers.mail import *
from flask import redirect


ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
api = Api(app)
mongo = PyMongo(app)
auth = HTTPBasicAuth()
#app.json_encoder = MongoEngineJSONEncoder
app.config['SECRET_KEY'] = 'valarMorghulis'


client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.test


#####################################Test Details
##chris - hello123
##john - bye123
##daanish - abcd1234
##daanish - hi123


@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify( { 'error': 'Bad request' } ), 400)

def hash_password(password):
	return pwd_context.encrypt(password)

def password_check(username, password):
	user = db.users.find_one({'username': username})
	hashed_password = user['password']
	return pwd_context.verify(password, hashed_password)    


@auth.verify_password       
def verify_password(username_or_token, password):
	# first try to authenticate by token
	user = verify_auth_token(username_or_token)
	if not user:
		# try to authenticate with username/password
		user = db.users.find_one({'username': username_or_token})
		if not user or not password_check(username_or_token, password):
			return False
	g.user = user
	return True     


def verify_auth_token(token):
	s = Serializer(app.config['SECRET_KEY'])

	try:
		data = s.loads(token)
	except SignatureExpired:
		return None # valid token, but expired
	except BadSignature:
		return None # invalid token
	user_id = data['id']
	user = db.users.find({'_id': ObjectId(user_id)})
	return user



def generate_auth_token(expiration = 600):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)

		user_id = str(g.user['_id'])
		return s.dumps({'id': user_id})       

				
@app.route('/api/v1/resource', methods = ['GET'])
@auth.login_required        
def get_user_detail():
	output = g.user
	output['_id'] = str(output['_id'])
	return jsonify({'result': output})

@app.route('/api/v1/token', methods = ['GET'])
@auth.login_required    
def get_auth_token():
	token = generate_auth_token()
	return jsonify({ 'token': token.decode('ascii') })



						
@app.route('/api/v1/users', methods = ['GET'])  
def get_all_users():
	output=[]
	for user in db.users.find():
		print (user)
		output.append({'inserted_id': str(user['_id']), 'username': user['username'], 'password': user['password']})
	return jsonify({'result': output})  


@app.route('/api/v1/users', methods = ['POST']) 
def new_user():
	username = request.json.get('username')
	password = request.json.get('password')
	if username is None or password is None:
		abort(400) # missing arguments
		
	user = db.users.find_one({'username': username})
	print(user)
	if user:
		abort(400) #existing user

	hashed_password = hash_password(password)
	new_user_details = db.users.insert_one({'username': username, 'password': hashed_password})
	inserted_id = str(new_user_details.inserted_id)
	output = {'username': username, 'password': hashed_password, 'inserted_id': inserted_id}
	return jsonify({'result': output})


@app.route('/api/v1/register/<string:token>', methods = ['PUT'])
def confirm_user(token):
	####if token is not None: ###user has click on the link sent in the verification email
	s = Serializer(app.config['SECRET_KEY'])
	try:
		data = s.loads(token.encode('utf-8'))
		print(data)
	except SignatureExpired:
		return jsonify(status = 'Not OK', message = 'Token has expired')

	except BadSignature:
		return jsonify(status = 'Not OK', message = 'Invalid token')		
	user_email = data['email']
	user = db.users.find_one({'email': user_email})
	if user:
		print(user)
		if user['confirmed']: ####user has already verified his account. This can happen is the user clicks on the verification link 
		##multiple times by mistake
			return jsonify(message = 'Account has already been verified')

		else:
			print(user)
			db.users.update({'email': user['email']}, {'$set': {'confirmed': True}})
			return jsonify(status = 'OK', message = 'Verification successful')
	else:
		return jsonify(status = 'Not OK', message = 'Verification failed')



@app.route('/api/v1/register', methods = ['POST'])
def register_user():

		email_address = request.json.get('email')
		username = request.json.get('username')
		password = request.json.get('password')
		if username is None or password is None or email_address is None:
			abort(400) # missing arguments
		user_name = db.users.find_one({'username': username})
		user_email = db.users.find_one({'email': email_address})
		if user_name or user_email:
			return jsonify(status = 'Not OK', message = 'user name or email address already exists')
			
		###now add the user to the data base
		hashed_password = hash_password(password)
		newDocument = db.users.insert_one({'username': username, 'password': hashed_password, 'email': email_address, 'confirmed': False})
		
		expiration = 3600
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		token = s.dumps({'email': email_address})

		string_token = token.decode('utf-8')
		print(string_token)
		
		content_email = "use this url for verification: http://localhost:9000/api/v1/register/" + string_token

		subject_line = "Verification Email"
		sender_email = "daanishraj@gmail.com"
		send_email(sender_email, email_address, subject_line, content_email)
		flash("You can now register! Please check your email")
		return jsonify(status = 'OK',message = 'email sent successfully')


# @app.route('/api/v1/register/token', methods = ['POST'])
# 	def verification(token):
# 	email_address = request.json.get('email')
# 	print("Please reenter your email address again")
# 	try:
# 		data = s.loads(token)
# 	except SignatureExpired:
# 		return None # valid token, but expired
# 	except BadSignature:
# 		return None # invalid token
# 	#user = User.query.get(data['id'])            
# 	user_email = data['confirm']
# 	if user_email == email_address:
# 		####do we need a boolean called confirm at this point?
# 		return jsonify(status = 'OK', message = 'Verification successful')

# 	else:
# 		return jsonify(status = 'Not OK', message = 'Verification failed')



def send_email(sender_email, receiver_email, subject_matter, content_email):
	sg = sendgrid.SendGridAPIClient(apikey = os.environ.get('SENDGRID_API_KEY'))
	mail = Mail(Email(sender_email), subject_matter, Email(receiver_email), Content("text/plain", content_email))
	response = sg.client.mail.send.post(request_body = mail.get())
	


	
@app.route('/api/v1/login', methods = ['POST'])
def login():	
	username = request.json.get('username')
	password = request.json.get('password')
	if username is None or password is None:
		abort(400) # missing arguments
	user = db.users.find_one({'username': username})
	if not user[confirmed]:
		return jsonify(status  = "Not OK", message = "Please Verify Your Account First")
	if verify_password(username, password):
		return jsonify(status  = "OK", message = "Login Successful!" )
	else:
		return jsonify(status  = "Not OK", message = "Login UnSuccessful - username or password are incorrect" )
			


########Forgot Password
@app.route('/api/v1/login/password', methods = ['POST'])
def forgot_password_link():
	email = request.json.get('email')
	if email is None:
		abort(400)
	user = db.users.find_one({'email': email})
	if not user:
		return jsonify(status  = "Not OK", message = "Invalid email")
	expiration = 3600
	s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
	token = s.dumps({'email': email})
	string_token = token.decode('utf-8')
	email_address = user['email']
	subject_line = "Password Reset"
	sender_email = "daanishraj@gmail.com"
	content_email = "Please click on the following url to reset your password: http://localhost:9000/api/v1/forgotpassword/" + string_token
	send_email(sender_email, email_address, subject_line, content_email)
	flash("You can now reset your password! Please check your email")
	return jsonify(status = 'OK',message = 'email sent successfully')


@app.route('/api/v1/forgotpassword/<string:token>', methods = ['POST'])
def forgot_reset_password(token):
	password = request.json.get('New password')
	password_again = request.json.get('Retype new password')
	s = Serializer(app.config['SECRET_KEY'])
	try:
		data = s.loads(token.encode('utf-8'))
		print(data)
	except SignatureExpired:
		return jsonify(status = 'Not OK', message = 'Link has expired')

	except BadSignature:
		return jsonify(status = 'Not OK', message = 'Invalid credentials')
	email = data['email']
	user = db.users.find_one({'email': email})
	if user:
		if password == password_again:
			hashed_password = hash_password(password)
			print(user)
			db.users.update({'email': email}, {'$set':{'password': hashed_password}})
			return jsonify(status = 'OK', message = 'Password has been successfully reset!')
		else:
			return jsonify(status = 'Not OK', message = 'Password mismatch')
	else:
		return jsonify(status = 'Not OK', message = 'Cannot reset password. Something went wrong!')



@app.route('/api/v1/resetpassword', methods = ['POST'])
@auth.login_required 
def reset_password():
	new_password = request.json.get('New password')
	new_password_again = request.json.get('Retype new password')
	email = g.user['email']
	if new_password == new_password_again:
		hashed_password = hash_password(new_password)
		db.users.update({'email': email}, {'$set':{'password': hashed_password}})
		user_new = db.users.find_one({'email': g.user['email']})
		return jsonify(status = 'OK', message = 'Password reset succesfully!')

	else:
		return jsonify(status = 'Not OK', message = 'Password mismatch!')

			
@app.route('/api/v1/test', methods = ['GET'])
@auth.login_required 
def test_function():
	print(g.user)
	flag = pwd_context.verify("abcd1234", g.user['password'])
	print(flag)
	return jsonify(status = 'OK')




			








if __name__ == '__main__':
	app.run(debug=True,port=9000)








