#!/bin/bash

# load from .env
source .env || {
    echo "Error: .env file not found"
    exit 1
}

# activate venv
if [ -d venv ]; then
    source venv/bin/activate || {
        echo "Error: venv not found"
        exit 1
    }
fi

python SocketServer.py \
    --host $HOST \
    --port $PORT \
    --stream $STREAM \
    --character $CHARACTER \
    --model ${MODEL:-"chatgpt-3.5"} \
    --proxy $PROXY \
    --APIKey $APIKEY \
    --APIBase $APIBASE
