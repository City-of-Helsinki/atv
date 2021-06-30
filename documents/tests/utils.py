from uuid import uuid4


def generate_tos_uuid():
    return str(uuid4()).replace("-", "")
