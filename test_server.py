import sys
import traceback

with open("error_debug.txt", "w") as f:
    f.write("Starting test_server.py execution...\n")
    try:
        import app
        f.write("Imported app successfully!\n")
        f.write("Running app.run()...\n")
        f.flush()
        app.app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    except Exception as e:
        f.write("EXCEPTION OCCURRED:\n")
        f.write(traceback.format_exc())
        f.flush()
