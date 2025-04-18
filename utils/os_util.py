import os
import sys
import platform

import psutil
import signal

python_exec = sys.executable or "python"
system = platform.system()


def kill_process(pid):
    if system == "Windows":
        cmd = "taskkill /t /f /pid %s" % pid
        ret = os.system(cmd)
        ret >>= 8
    else:
        _kill_proc_tree(pid)


def _kill_proc_tree(pid, including_parent=True):
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        # Process already terminated
        return

    children = parent.children(recursive=True)
    for child in children:
        try:
            os.kill(child.pid, signal.SIGTERM)  # or signal.SIGKILL
        except OSError:
            pass
    if including_parent:
        try:
            os.kill(parent.pid, signal.SIGTERM)  # or signal.SIGKILL
        except OSError:
            pass


runtime_dir = os.environ.get("roppongi_root", "./")
