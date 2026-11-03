from http import HTTPStatus
import requests

class TestRig:
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