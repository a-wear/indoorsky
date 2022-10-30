#!/bin/sh

# go to directory where the app is
cd /preprocessingapp
# start gunicorn
exec gunicorn --bind :5000 run:app --certfile ./certs/cert.pem --keyfile ./certs/privkey.pem