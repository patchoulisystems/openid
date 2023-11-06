## OpenConnect ID Demo

### Service Config
1. You will need to go to the following URL and create a new project.  
https://console.cloud.google.com/apis
2. Open the sidebar > APIs & Services > OAuth Consent form  
3. Follow the instructions and create credentials to get your Client ID and set Redirect URI and replace them at the top of `app.py`  
4. You should also get a client secret which can be put into a docker secret below  


### Build
`sudo docker build -t oiddemo .`

### Create flask secret  
`python -c 'import secrets; print(secrets.token_hex())' | docker secret create FLASK_SECRET -`
### Create client secret
`printf <CLIENT SECRET HERE> | docker secret create CLIENT_SECRET -`
### Run
If you want to run as a standalone container you will need to edit the code at the top of `app.py` to use something other than docker secrets  
`sudo docker run -p 8080:5000 oiddemo:latest`

Otherwise you can run this as a service  
`docker service create --name oiddemo --publish 8080:5000 --secret CLIENT_SECRET --secret FLASK_SECRET oiddemo:latest`