#!/bin/bash

function install_dependencies() {
    git submodule update --init --recursive
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    pip install -r requirements.txt
}

# load from .env
source .env || {
    echo "Error: .env file not found"
    exit 1
}

# activate venv if exists
if [ -d .venv ]; then
    source .venv/bin/activate || {
        echo "Error: .venv activate failed"
        exit 1
    }
    # Add CUDA libraries to LD_LIBRARY_PATH
    export LD_LIBRARY_PATH="$PWD/.venv/lib/python3.10/site-packages/nvidia/cuda_runtime/lib:$PWD/.venv/lib/python3.10/site-packages/torchvision.libs:$LD_LIBRARY_PATH"
elif [ -d venv ]; then
    source venv/bin/activate || {
        echo "Error: venv activate failed"
        exit 1
    }
    # Add CUDA libraries to LD_LIBRARY_PATH
    export LD_LIBRARY_PATH="$PWD/venv/lib/python3.10/site-packages/nvidia/cuda_runtime/lib:$PWD/venv/lib/python3.10/site-packages/torchvision.libs:$LD_LIBRARY_PATH"
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
