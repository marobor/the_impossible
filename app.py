from flask import Flask
from website import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


def hello_world():  # put application's code here
    return 'Hello World!'
