import torch
import os

is_half_str = os.environ.get("is_half", "True")
is_half = True if is_half_str.lower() == 'true' else False

if torch.cuda.is_available():
    infer_device = "cuda"
else:
    infer_device = "cpu"

if infer_device == "cuda":
    gpu_name = torch.cuda.get_device_name(0)
    if (
            ("16" in gpu_name and "V100" not in gpu_name.upper())
            or "P40" in gpu_name.upper()
            or "P10" in gpu_name.upper()
            or "1060" in gpu_name
            or "1070" in gpu_name
            or "1080" in gpu_name
    ):
        is_half = False

if infer_device == "cpu":
    is_half = False
