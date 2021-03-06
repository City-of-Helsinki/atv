from uuid import UUID


def is_valid_uuid(uuid_string: str, version: int = 4):
    """
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.

    Taken from https://gist.github.com/ShawnMilo/7777304
    """

    try:
        val = UUID(uuid_string, version=version)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

    # If the uuid_string is a valid hex code,
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a
    # valid uuid4. This is bad for validation purposes.

    return str(val.hex) == uuid_string.replace("-", "")
