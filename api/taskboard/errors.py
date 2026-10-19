"""Every error is JSON: {"error": "what went wrong"}, with the right status code."""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """raise ApiError(404, "not found") anywhere in a view"""

    def __init__(self, status, message, **extra):
        super().__init__(message)
        self.status, self.message, self.extra = status, message, extra


def register(app):
    @app.errorhandler(ApiError)
    def api_error(e):
        return jsonify(error=e.message, **e.extra), e.status

    @app.errorhandler(HTTPException)
    def http_error(e):                       # 404 for an unknown URL, 405 for a wrong method, ...
        return jsonify(error=e.name.lower()), e.code
