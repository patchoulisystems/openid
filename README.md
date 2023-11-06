## OpenConnect ID Demo

### Build
`sudo docker build -t oiddemo .`

### Create flask secret  
`python -c 'import secrets; print(secrets.token_hex())' | docker secret create FLASK_SECRET -`
### Create client secret
`echo <CLIENT SECRET HERE> | docker secret create CLIENT_SECRET -`
### Run
`sudo docker run -p 8080:5000 oiddemo:latest`