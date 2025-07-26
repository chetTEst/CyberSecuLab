import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(app, debug=True, host='0.0.0.0', port=8000)