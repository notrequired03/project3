import threading
import time
import requests
from waitress import serve
from app import app

def run_srv():
    serve(app, host="127.0.0.1", port=5000)

t = threading.Thread(target=run_srv, daemon=True)
t.start()

time.sleep(2)

try:
    r = requests.get("http://127.0.0.1:5000/api/config")
    print("SUCCESSFULLY CONNECTED TO IN-PROCESS WAITRESS SERVER!")
    print("STATUS:", r.status_code)
    print("JSON:", r.json())
except Exception as e:
    print("FAILED TO CONNECT TO WAITRESS SERVER:", e)
