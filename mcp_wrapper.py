#!/usr/bin/env python3
import subprocess
import sys
import os

# Path to the virtual environment python
VENV_PYTHON = "/Users/darren_dean/projects/miraculous-maids-demo/.venv/bin/python"

# Log to a file to capture startup errors
log = open("/Users/darren_dean/projects/miraculous-maids-demo/mcp_startup.log", "w")

try:
    # Use the venv python to ensure all dependencies are found
    cmd = [VENV_PYTHON, "/Users/darren_dean/projects/miraculous-maids-demo/mcp_jobber_server.py"]
    
    proc = subprocess.Popen(
        cmd,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=log
    )
    proc.wait()
except Exception as e:
    log.write(str(e))
finally:
    log.close()
