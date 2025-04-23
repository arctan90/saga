python3.10 -m venv .venv
source .venv/bin/activate
export NO_TORCH_COMPILE=1

nohup python main.py --saga &
