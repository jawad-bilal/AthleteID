"""
WSGI entry point for PythonAnywhere.

In the PythonAnywhere Web tab, set the WSGI file to this path
(after you clone the repo), e.g.:

  /home/<your-username>/AthleteID/server/wsgi.py
"""
import os
import sys

# Folder that contains server.py, util.py, wavelet.py
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

# Ensure working directory is server/ so relative artifact paths stay valid
os.chdir(SERVER_DIR)

from server import app as application  # noqa: E402
