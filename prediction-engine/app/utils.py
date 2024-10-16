from flask import request, abort


def extract_and_validate_url():
    """
    Extracts the 'url' parameter from the request and validates its presence.
    If the 'url' is not present, it aborts the request with a 400 error.

    Returns:
        str: The extracted URL if it is present.
    """
    url = request.json.get("url")
    if not url:
        abort(400, description="Invalid request: 'url' is required")
    return url
