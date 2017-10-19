
"""This is the code for a Student REST API"""

from flask import Flask
from flask_restful import Resource, Api
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson import ObjectId
from requests import put, get
from flask_restful import reqparse
import unittest
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient()
client = MongoClient('localhost', 27017)
#client = MongoClient('mongodb://localhost:27017/')
db = client['students']
student_info_collection = db.studentInfo



class Student(Resource):

	"""
		Parameters
		----------
		name : string, optional
				name of a student in the database
		Returns		
		-----------
		dictionary
				   details of student in the database
	"""
		   
	def get(self, name=None):
		"""Get the details of all 
		students in the data base
		"""
		output=[]
		if name is None:
			for student in student_info_collection.find():
				output.append({'name': student['name'], 'age': student['age'], 'phone': student['phone']})
			return jsonify({'result': output})
		else:
			student=student_info_collection.find_one({'name':name})
			if student:
				output = {'name': student['name'], 'age': student['age'], 'phone': student['phone']}
			else:
				output= "This student is not in the data base"	
			return jsonify({'result' : output})

	"""
		Parameters
		----------

		Returns		
		-----------
		dictionary
				   details of student who the user has added to the data base	
	"""

	def post(self):
		"""Add details of a student 
		the student data base
		"""
		name = request.json['name']
		age = request.json['age']
		phone = request.json['phone']
		new_student = student_info_collection.insert_one({'name': name, 'age': age, 'phone': phone})
		output = {'name': name, 'age': age, 'phone': phone, 'inserted_id':str(new_student.inserted_id)}
		return jsonify({'result': output})	
	"""
		Parameters
		----------

		name: string
			  name of a student in the database

		Returns		
		-----------
		dictionary
				   details of student who's information the user has added to the data base	
	"""		

	def put(self, new_name):
		"""Update details of a student
		in the student data base
		"""
		# if "name" in request.json:
		if student_info_collection.find_one({'name': name}) is not None:
			new_name=request.json['name']
			new_age=request.json['age']
			new_phone=request.json['phone']

			student_info_collection.update_one({'name': name}, {'$set':{'name':new_name, 'age':new_age,'phone':new_phone}})
			return jsonify(status = 'OK',message = 'updated successfully')


		else:
			return "Sorry, such a student does not exist in database"		




		# if "name" in request.json:
		# 	new_name = request.json['name']
		# else:
		# 	return "No name"
		# if "age" in request.json:
		# 	age = request.json['age']
		# else:
		# 	return
		# if "phone" in request.json:
		# 	phone=request.json['phone']
		# else:
		# 	return
		# if student_info_collection.find_one({'name': name}):
		# 	student_info_collection.update_one({'name': name}, {'$set':{'name':new_name, 'age':age,'phone':phone}})
		# else:
		# 	return "Student does not exist"
		# return jsonify(status = 'OK',message = 'updated successfully')

	"""
		Parameters
		----------

		name: string
			  name of a student in the database

		Returns		
		-----------
			status message
	"""			

	def delete(self, name):
		"""delete details of a student
		from the student data base
		"""
	
		if student_info_collection.find_one({'name': name}) is not None:
			student_info_collection.delete_one({'name': name})
			return jsonify(status = 'OK', message ='deletion successful')
		else:
			return jsonify(status = 'FAIL',message = 'deletion  unsuccessful  - student not found in data base')


api.add_resource(Student, '/api/v1','/api/v1/<string:name>')



if __name__ == '__main__':
	app.run(debug=True)







