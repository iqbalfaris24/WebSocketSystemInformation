import sys
import os

venv_path = '/var/python/WebSocketSystemInformation/env/bin/python'

sys.path.insert(0, '/var/python/WebSocketSystemInformation')

from system import app as application
