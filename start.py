import sys
from app import app

print("==========================================", flush=True)
print("Starting ChatHere Twitter Bot Server on http://127.0.0.1:5000", flush=True)
print("==========================================", flush=True)

app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
