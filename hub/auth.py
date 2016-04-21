import sys
import hub
import logger
import json
import requests
dev_url = 'https://dev.api.stratusprint.com/v1/'


def hub_sign_in(api_key, base_url = dev_url):
    #uses api key to get headers for commands, and signs in
    log = hub.log
    url =  base_url + 'hub_auth/sign_in'
    header = { 'Content-Type' : 'application/json',
            'Accept': 'application/json' , 'Authorization': api_key }
    try:
        r = requests.post(url, headers = header, timeout=10)
    except requests.ConnectionError:
        log.log("ERROR: Could not connect to "
                + url + ". Trying to sign in.")
        return None
    except requests.exceptions.Timeout:
        log.log("ERROR: Connection timed out with "
                + url + ". Trying to sign in.")
        return None
    if r.status_code == requests.codes.unauthorized:
        log.log("ERROR: Bad status code when signing in. "
                + str(r.status_code) + "API Key is most likely invalid.")
        return None
    elif r.status_code == requests.codes.ok:
        res_header = r.headers;
        try:
            headers = {
                    'access-token' : res_header['access-token'],
                    'uid': res_header['uid'],
                    'token-type': res_header['token-type'],
                    'client' : res_header['client'],
                    'cache-control': "no-cache",
            }
        except KeyError:
            log.log("ERROR: Headers for signin on " 
                    + url + " did not contain necessary information.")
        return headers
    return None
        
def hub_sign_out(headers, base_url = dev_url):
    #signs out and invalidates tokens forever
    log = hub.log
    url = base_url + 'hub_auth/sign_out'
    try:
            r = requests.delete(url, headers = headers, timeout=10)
    except requests.ConnectionError:
        log.log("ERROR: Could not connect to "
                + url + ". Trying to sign out.")
        return False
    except requests.exceptions.Timeout:
        log.log("ERROR: Connection timed out with "
                + url + ". Trying to sign out.")
        return False
    if r.status_code == requests.codes.created:
        return True
    return False

def get_headers(api_key, headers=None, base_url = dev_url):
    #checks validation and signs in once again
    #return { 'Content-Type' : 'application/json',
    #        'Accept': 'application/json' , 'Authorization': api_key }
    log = hub.log
    #TODO Make sure this doesn't make communication super slow.
    # Might need caching
    if headers == None:
        return hub_sign_in(api_key, base_url=base_url)
    url = base_url + 'hub_auth/validate_token'
    try:
            r = requests.get(url, headers = headers, timeout=10)
    except requests.ConnectionError:
        log.log("ERROR: Could not connect to "
                + url + ". Trying to validate headers.")
        return None
    except requests.exceptions.Timeout:
        log.log("ERROR: Connection timed out with "
                + url + ". Trying to validate headers.")
        return None
    if r.status_code == requests.codes.unauthorized:
            headers = hub_sign_in(api_key, base_url=base_url)
    return headers

if __name__ == "__main__":
    api_key = sys.argv[1]
    if api_key == None:
        print("error, need api_key")
        exit(1)
    headers = get_headers(api_key)
    print str(headers)
    print str(get_headers(api_key, headers))
