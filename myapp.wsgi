import sys
import os

venv_path = '/var/python/system/env/bin/python'

sys.path.insert(0, '/var/python/system')

from system import app as application
