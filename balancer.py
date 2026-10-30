import threading
import requests
from flask import Flask, Response

import time
from datetime import datetime, UTC

from http import HTTPStatus

from servers import Server
from tables import create_server_health_table


class LoadBalancer:
    def __init__(self, servers, port):
        self.servers = servers
        self.port = port
        self.lock = threading.Lock()
        self.current_server_index = 0
        self.server_health = {server.name: False for server in self.servers}

        self.app = Flask("LoadBalancer")


        @self.app.route("/")
        def index():
            return "Hi! Im the load balancer"


        @self.app.route("/health")
        def health():
            selected_server = self.get_next_server()
            return self.forward_request(selected_server, "/health")


    def activate(self):
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
            name = server.name
            response = self.forward_request(server, "/health")
            status = HTTPStatus(response.status_code)
            server_info.append(
                {
                    "name": name,
                    "status_value": status.value,
                    "status_phrase": status.phrase
                }
            )

            server_health[name] = status == HTTPStatus.OK

        create_server_health_table(server_info)

        with self.lock:
            self.server_health = server_health
        

if __name__ == '__main__':

    SERVER_A = Server("SERVER_A", 9001)
    SERVER_B = Server("SERVER_B", 9002)
    SERVER_C = Server("SERVER_C", 9003)


    server_list = [SERVER_A, SERVER_B, SERVER_C]
    lb = LoadBalancer(server_list, 8000)


    thread_a = threading.Thread(target=SERVER_A.activate)
    thread_a.start()

    thread_b = threading.Thread(target=SERVER_B.activate)
    thread_b.start()

    thread_c = threading.Thread(target=SERVER_C.activate)
    thread_c.start()

    thread_lb = threading.Thread(target=lb.activate)
    thread_lb.start()


    time.sleep(2)
    lb.health_check()