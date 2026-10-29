from flask import Flask, jsonify
from datetime import datetime, UTC

class Server:

    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.app = Flask(self.name)


        @self.app.route("/")
        def index():
            return "Hello!"


        @self.app.route("/health")
        def health():
            return jsonify({
                "server": self.name,
                "status": "ok",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            })


    def activate(self):
        self.app.run(port=self.port, use_reloader=False)


