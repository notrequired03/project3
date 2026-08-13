import sys
import os
import traceback
from waitress import serve

err_log = os.path.join(os.path.dirname(__file__), "server_error.txt")

f = open(err_log, "w", encoding="utf-8")
f.write("Starting run_server.py...\n")
f.flush()

try:
    f.write("Importing app...\n")
    f.flush()
    from app import app
    f.write("Starting serve(app, host='127.0.0.1', port=5000)...\n")
    f.flush()
    serve(app, host="127.0.0.1", port=5000)
except Exception as e:
    f.write("FATAL EXCEPTION:\n")
    f.write(traceback.format_exc())
    f.flush()
