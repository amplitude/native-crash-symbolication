#!/bin/bash

source .env/bin/activate
exec python server.py $@
deactivate
