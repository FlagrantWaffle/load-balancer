from http import HTTPStatus
import requests

class TestRig:


    def restore_servers(self, lb_port, server=None):
        response = requests.get(
            f"http://127.0.0.1:{lb_port}/backends",
            timeout=3
        )
        response.raise_for_status()

        servers = response.json()

        if server is not None:
            if server not in servers:
                raise ValueError(f"Unknown server: {server}")

            servers = {server: servers[server]}

        for server_name, port in servers.items():
            print(f"Attempting to restore {server_name}")

            restore_response = requests.post(
                f"http://127.0.0.1:{port}/__test/restore",
                json={"error": None},
                timeout=3
            )
            restore_response.raise_for_status()



    def produce_503(self, lb, lb_port, server):
        print("args received, attempting to produce 503 error")

        backends_response = requests.get(
            f"http://127.0.0.1:{int(lb_port)}/backends",
            timeout=3
        )

        backends_response.raise_for_status()
        servers = backends_response.json()
        server_port = servers[server]

        post_response = requests.post(
            url = f"http://127.0.0.1:{int(server_port)}/__test/error",
            json = {
                "error": 503,
            },
            timeout = 3
        )