import hmac
import json
from hashlib import sha256
import re

import config


def validate_form_data(byte_str: bytes, required_fields: list):
    decoded_str = byte_str.decode('utf-8')
    try:
        data = json.loads(decoded_str)
    except json.decoder.JSONDecodeError as e:
        return None, "It is not JSON data"

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return None, f"{', '.join(missing_fields)} field(s) is missing"
    else:
        return data, None


def get_user_hash(data, secret_key=config.secret_key):
    data_check_string = "\n".join([f"{key}={value}" for key, value in sorted(data.items()) if value is not None])
    user_hash = hmac.new(sha256(secret_key.encode()).digest(), data_check_string.encode(), sha256).hexdigest()

    return user_hash


def is_valid_email(email):
    email_regex = r'^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-]+$'
    return re.match(email_regex, email) is not None
