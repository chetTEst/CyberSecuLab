# __init__.py
from flask import Flask

app = Flask(__name__)

# Register routes
from . import routes

# Run the application
if __name__ == '__main__':
    app.run()
