#!/bin/bash

date=`date`
echo " * STARTING a new deployment on $date."

echo " * Waiting 15 seconds to give time to our server to reply to GitHub..."
# This is to give time to the server to reply to GitHub, since the next command
# `sv stop webapp` will stop our webserver.
sleep 15

echo " * Stopping the webapp service..."
sv stop webapp

echo " * Pulling new code..."
git pull

echo " * Starting the webapp service..."
# During a webapp start, the script `run-webapp.sh` is run, which performs:
# - db migration
# - run management command `initialize_site`
# - collect static files
sv start webapp

date=`date`
echo " * END of the deployment on $date."
echo