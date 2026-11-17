from functools import wraps
import hmac
import os

from dotenv import load_dotenv
from flask import request, jsonify

load_dotenv()
FAULT_INJECTION_TOKEN = os.getenv("FAULT_INJECTION_TOKEN")
FAULT_INJECTION_ACTIVE = os.getenv("FAULT_INJECTION_ACTIVE", "0") == "1"


def require_fault_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        scheme, separator, token = auth_header.partition(" ")

        if (
            
            not FAULT_INJECTION_ACTIVE
            or not FAULT_INJECTION_TOKEN
            or scheme.lower() != "bearer"
            or not token
            or not hmac.compare_digest(token, FAULT_INJECTION_TOKEN)):

            return jsonify({"error": "Unauthorized"}), 401


        return func(*args, **kwargs)

    return wrapper