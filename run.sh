#!/bin/bash
SCRIPT_NAME=SocketServer.py
PROXY=
STREAM=False
CHARACTER=paimon

APIBASE=
APIKEY=xxx
MODEL=chatgpt-3.5

source venv/bin/activate
python $SCRIPT_NAME --stream $STREAM --character $CHARACTER --model $MODEL --proxy $PROXY --APIKey $APIKEY --APIBase $APIBASE
