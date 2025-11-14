import numpy as np
import time
import os

def scalar(val):
    if np.isscalar(val):
        return float(val)
    elif isinstance(val, np.ndarray):
        return float(val.flatten()[0])
    else:
        return float(val)

def make_dirs():
    os.makedirs("captures", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def timestamp():
    return time.strftime("%Y%m%d_%H%M%S")
