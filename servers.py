from flask import Flask, jsonify, request
from datetime import datetime, UTC
from http import HTTPStatus

class Server:

    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.app = Flask(self.name)
        self.error = None


        @self.app.route("/")
        def index():
            return "Hello!"


        @self.app.route("/health")
        def health():
            if self.error is not None:
                return "Simulated backend failure", int(self.error)
            
            return jsonify({
                "server": self.name,
                "status": "ok",
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            })

        @self.app.post("/__test/error")
        def inject_error():
            data = request.get_json(silent=True) or {}

            if data.get("error") != 503:
                return jsonify({"error": "Unsupported error code"}), 400

            self.error = HTTPStatus.SERVICE_UNAVAILABLE

            return "", 204




    def activate(self):
        self.app.run(port=self.port, use_reloader=False)


