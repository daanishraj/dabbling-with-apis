"""Integrate our app with the USAepay API so the user can pay us, the merchant"""

from flask import Flask
from flask import jsonify
from flask import request
import requests
import hashlib
import base64
import json
import ast

app = Flask(__name__)


seed = "abcdefghijklmnop"
apikey = "_XtqQa8R8j79O5270d161vDs5454hMKp" 
apipin = "12345"
prehash = apikey + seed + apipin
prehash = prehash.encode('utf8')
hash_val = hashlib.sha256(prehash).hexdigest()


apihash = "s2/" + seed + "/" + hash_val
str_val = apikey + ":" + apihash
authkey = base64.b64encode(str_val.encode('utf-8'))

amount_val = "20.00"
tax_val = "1.00"
tip_val = "0.50"
invoice_num = "12356" 


@app.route('/payments', methods=['POST'])
def post():
	cardholder_name = request.json['cardholder']
	cc_number = request.json['number']
	expiration_date = request.json['expiration']
	cvc_num = request.json['cvc']
	avs_street_addr = request.json['avs_street']
	avs_zip_num = request.json['avs_zip']	
	
	payload_1 = {
	'command': 'cc:save', 
	'redir': 'localhost:5000/verification', 
	'key': apikey, 
	'hash': hash_val,
	'card': cc_number,
	'expir': expiration_date
	}

	print(type(cc_number))

	headers = {"User-Agent": "uelib v6.8", "Content-type": "application/json", "Authorization": "Basic " + authkey.decode('utf-8')}

	r_1 = requests.post("https://sandbox.usaepay.com/api/v2/transactions", json = payload_1, headers = headers)
	
	response_data_1 = r_1.json()
	

	return jsonify(response_data_1)

	


# @app.route('/payments', methods=['POST'])
# def post():
# 	cardholder_name = request.json['cardholder']
# 	cc_number = request.json['number']
# 	expiration_date = request.json['expiration']
# 	cvc_num = request.json['cvc']
# 	avs_street_addr = request.json['avs_street']
# 	avs_zip_num = request.json['avs_zip']
# 	payload = {'command': 'cc:sale', 'amount': amount_val, 'amount_detail': {'tax': tax_val, 'tip': tip_val},
# 	'creditcard': {'cardholder': cardholder_name, 'number': cc_number, 'expiration': expiration_date, 'cvc': cvc_num, 'avs_street': avs_street_addr,
# 	'avs_zip': avs_zip_num},
# 	'invoice': invoice_num}
# 	headers = {"User-Agent": "uelib v6.8", "Content-type": "application/json", "Authorization": "Basic " + authkey.decode('utf-8')}
# 	#headers = {"User-Agent: uelib v6.8", "Content-type: application/json", auth_item}

# 	#return requests.post("https://sandbox.usaepay.com/api/v2/transactions", json = payload)
# 	r = requests.post("https://sandbox.usaepay.com/api/v2/transactions", json = payload, headers = headers)
	
# 	return jsonify(json.loads(r.text))
	



if __name__ == '__main__':
	app.run(debug=True, port = 7000)





