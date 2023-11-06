# syntax=docker/dockerfile:1
FROM python
RUN pip3 install flask google-api-python-client pyjwt[crypto]
WORKDIR /openid
COPY . .
#ENTRYPOINT [ "/bin/bash" ]

ENTRYPOINT [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]