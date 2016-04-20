import requests
import json
base_url = 'https://dev.api.stratusprint.com/v1/';
api_key = '';
headers = []

def hub_sign_in(): #uses api key to get headers for commands, and signs in
	url =  base_url + 'hub_auth/sign_in'
	header = { 'Content-Type' : 'application/json', 'Accept': 'application/json' , 'Authorization': api_key }
	print "Signing In..."
	try:
		r = requests.post(url, headers = header );
	except:
		print "Couldn't Sign In"
	print"Signed in Successfully"
	res_header = r.headers;
	global headers
	headers = {
		'access-token' : res_header['access-token'],
		'uid': res_header['uid'],
		'token-type': res_header['token-type'],
		'client' : res_header['client'],
		'cache-control': "no-cache",
	};
	#print( r.text )
	
def hub_sign_out(): #signs out and invalidates tokens forever
	print "Signing Out..."
	url = base_url + 'hub_auth/sign_out'
	#print(headers)
	try:
		r = requests.request("DELETE",url,headers = headers);
	except:
		"Couldn't Sign Out"
	print "Signed Out Successfully"
	#print ( r.text)

def revalidate(): #checks validation and signs in once again
	url = base_url + 'hub_auth/validate_token'
	print "Determining Token Validation..."
	try:
		r = requests.request("GET",url,headers = headers);
	except:
		print "Could Not Be Determined"
	print "Status_code:", r.status_code
	if r.status_code == 401:
		print "Token invalid, Signing in again"
		hub_sign_in()
	else:
		print "Token Is Valid"

hub_sign_in()
hub_sign_out()
revalidate();







