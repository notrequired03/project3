import sys
from app import app

if __name__ == "__main__":
    print("==========================================", flush=True)
    print("  ChatHere.online Twitter AI Bot Dashboard", flush=True)
    print("  Server running on http://localhost:5000  ", flush=True)
    print("==========================================", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
