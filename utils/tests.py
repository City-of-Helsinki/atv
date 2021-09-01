def assert_in_errors(message, response: dict):
    assert "errors" in response
    assert str(message) in response.get("errors")
