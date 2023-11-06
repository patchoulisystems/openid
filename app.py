from flask import Flask, session, make_response, request, render_template, redirect
import hashlib
import os
import requests
import urllib.parse
import json
import jwt
import base64

app = Flask(__name__)
CLIENT_ID = '684917651846-coqm1o7h4ujbaridhd0v5f065a01ons3.apps.googleusercontent.com'
# get secrets
f = open('/run/secrets/CLIENT_SECRET', "r")
CLIENT_SECRET = f.read()
f.close()
f = open('/run/secrets/FLASK_SECRET', "rb")
app.secret_key = f.read()
f.close()
APPLICATION_NAME = 'OIDDEMO'
#REDIRECT_URI = 'http://localhost:8080'
REDIRECT_URI = 'http://m29.c3310.cyber.uml.edu:8080'

@app.route('/', methods=['GET', 'POST'])
def basePage():
    STATE = request.args.get('state', '')
    code = request.args.get('code','')
    match request.method:
        case 'GET':
            # check to see if returning from an Auth attempt
            if not STATE:
                return make_response(
                    render_template('index.html',
                                    CLIENT_ID=CLIENT_ID,
                                    STATE=STATE,
                                    CODE=code,
                                    STATUS='OK',
                                    APPLICATION_NAME=APPLICATION_NAME))
            # check incoming state vs stored state
            elif STATE != session['state']:
                return make_response(
                    render_template('index.html',
                                    CLIENT_ID=CLIENT_ID,
                                    STATE=STATE,
                                    CODE=code,
                                    STATUS='Error Invalid State',
                                    APPLICATION_NAME=APPLICATION_NAME))
            else:
                # successful auth callback
                session['code'] = code
                return make_response(
                    render_template('index.html',
                                    CLIENT_ID=CLIENT_ID,
                                    STATE=STATE,
                                    CODE=code,
                                    STATUS='Auth Code Received',
                                    APPLICATION_NAME=APPLICATION_NAME))
        case 'POST':
            # Create a state token to prevent request forgery.
            # Store it in the session for later validation.
            # Set the client ID, token state, and application name in the HTML while
            # serving it.
            state = hashlib.sha256(os.urandom(1024)).hexdigest()
            session['state'] = state
            if request.form.get('Acquire Auth') == 'Acquire Auth':
                # if we have a token just get ID, else authenticate first
                if session.get('code'):
                    # get id
                    oidc_config = requests.get('https://accounts.google.com/.well-known/openid-configuration').json()
                    tokenUrl = oidc_config['token_endpoint']
                    signing_algos = oidc_config["id_token_signing_alg_values_supported"]
                    # setup a PyJWKClient to get the appropriate signing key
                    jwks_client = jwt.PyJWKClient(oidc_config["jwks_uri"])
                    params = {
                        'code': session['code'],
                        'client_id': CLIENT_ID,
                        'client_secret': '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',
                        'redirect_uri': REDIRECT_URI,
                        'grant_type': 'authorization_code'
                    }
                    tokenUrl = tokenUrl + '?' + urllib.parse.urlencode(params)
                    token = requests.post(tokenUrl).json()
                    if 'id_token' not in token:
                        # auth expired
                        return authRedirect(state)
                    table = '<h2>Result from Google OID<h2/><table width="500" border="1"><tr><th>Key</th><th>Value</th></tr>'
                    for k, v in token.items():
                        table += f'<tr><td>{k}</td><td>{v}</td></tr>'
                    table += '</table>'
                    
                    #decode payload
                    id_token = token["id_token"]
                    # get signing_key from id_token
                    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
                    access_token = token["access_token"]
                    payload = jwt.decode(
                        id_token,
                        key=signing_key.key,
                        algorithms=signing_algos,
                        audience=CLIENT_ID,
                    )
                    # could not get the header properly out of decode_complete
                    #payload, header = data["payload"], data["header"]
                    ## get the pyjwt algorithm object
                    #alg_obj = jwt.get_algorithm_by_name(header["alg"])

                    ## compute at_hash, then validate / assert
                    #digest = alg_obj.compute_hash_digest(access_token)
                    #at_hash = base64.urlsafe_b64encode(digest[: (len(digest) // 2)]).rstrip("=")
                    #assert at_hash == payload["at_hash"]

                    table += '<h2>JWT Payload<h2/><table width="500" border="1"><tr><th>Key</th><th>Value</th></tr>'
                    for k, v in payload.items():
                        table += f'<tr><td>{k}</td><td>{v}</td></tr>'
                    table += '</table>'
                    return table
                else:
                    return authRedirect(state)
            elif request.form.get('Clear Session') == 'Clear Session':
                session.clear()
                return make_response(
                    render_template('index.html',
                                    CLIENT_ID=CLIENT_ID,
                                    STATE=STATE,
                                    CODE=code,
                                    STATUS='Session Cleared',
                                    APPLICATION_NAME=APPLICATION_NAME))

def authRedirect(state):
    url = 'https://accounts.google.com/o/oauth2/v2/auth?'
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': 'openid email',
        'redirect_uri': REDIRECT_URI,
        'state': state
        #'nonce': '0394852-3190485-2490358',
    }
    url = url + urllib.parse.urlencode(params)
    return redirect(url)

if __name__ == "__main__":
    app.run(debug=True)
