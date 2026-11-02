import threading
import requests
from flask import Flask, Response

import time
from datetime import datetime, UTC

from http import HTTPStatus

from servers import Server
from tables import create_server_health_table

import logging

class LoadBalancer:
    def __init__(self, servers, port):
        self.servers = servers
        self.port = port
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.current_server_index = 0
        self.server_health = {server.name: False for server in self.servers}

        self.app = Flask("LoadBalancer")



        @self.app.route("/")
        def index():
            return 'Hi! Im the load balancer <br> <a href="/health">Health</a>'


        @self.app.route("/health")
        def health():
            selected_server = self.get_next_server()
            return self.forward_request(selected_server, "/health")


    def activate(self):

        for server in self.servers:
            thread = threading.Thread(
                target=server.activate,
                name=server.name,
                daemon=True
            )
            thread.start()

        health_thread = threading.Thread(
            target=self.monitor_health,
            name="HealthMonitor",
            daemon=True
        )
        health_thread.start()

        self.app.run(port=self.port, use_reloader=False)



    def get_next_server_round_robin(self):

        with self.lock:
            healthy_servers = [
                server for server in self.servers if self.server_health[server.name]
            ]

            if len(healthy_servers) > 0:
                self.current_server_index %= len(healthy_servers)
                server = healthy_servers[self.current_server_index]
                self.current_server_index = (self.current_server_index + 1) % len(healthy_servers)

                return server

            return None

    def get_next_server(self):
        return self.get_next_server_round_robin()


    def forward_request(self, selected_server, endpoint):

        if selected_server is None:
            return Response(
                "No servers available for load balancing",
                status=HTTPStatus.SERVICE_UNAVAILABLE
            )

        url = f"http://127.0.0.1:{selected_server.port}{endpoint}"


        try:
            response = requests.get(url, timeout=3)
            status = response.status_code

        except requests.exceptions.Timeout:
            return Response(
                "Backend server timed out",
                status=HTTPStatus.GATEWAY_TIMEOUT
            )

        except requests.exceptions.ConnectionError:
            with self.lock:
                self.server_health[selected_server.name] = False

            return Response(
                "Backend server could not be reached",
                status=HTTPStatus.BAD_GATEWAY
            )

        else:
            return Response(
                response.content,
                status = status,
                content_type = response.headers.get("Content-Type")
            )

    def health_check(self):
        server_info = []
        server_health = {}

        for server in self.servers:
            try:
                response = self.forward_request(server, "/health")
                status_code = response.status_code

                try:
                    status_phrase = HTTPStatus(status_code).phrase
                except ValueError:
                    status_phrase = "Unknown HTTP status"

                server_info.append({
                    "name": server.name,
                    "status_value": status_code,
                    "status_phrase": status_phrase
                })

                server_health[server.name] = status_code == HTTPStatus.OK

            except Exception:
                logging.exception(
                    "Health check failed for %s", server.name
                )

                server_health[server.name] = False

                server_info.append({
                    "name": server.name,
                    "status_value": "N/A",
                    "status_phrase": "Health check failed"
                })

        with self.lock:
            self.server_health = server_health

        create_server_health_table(server_info)


    def monitor_health(self):
        while not self.stop_event.is_set():
            try:
                self.health_check()

            except Exception:
                logging.exception("Health monitor encountered an error")

            self.stop_event.wait(5)


if __name__ == '__main__':

    SERVER_A = Server("SERVER_A", 9001)
    SERVER_B = Server("SERVER_B", 9002)
    SERVER_C = Server("SERVER_C", 9003)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    server_list = [SERVER_A, SERVER_B, SERVER_C]
    lb = LoadBalancer(server_list, 8000)
    lb.activate()