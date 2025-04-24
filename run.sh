#!/bin/bash
cd $HOME/git/saga || exit 1  # Exit if the directory doesn't exist

pid=$(ps -ef | grep main.py | grep saga | awk '{print $2}')
if [ -n "$pid" ]; then
    kill -9 $pid
    echo "Killed existing process: $pid"
else
    echo "No existing process found"
fi

python3.10 -m venv .venv
source .venv/bin/activate
export NO_TORCH_COMPILE=1

nohup python main.py --saga &
