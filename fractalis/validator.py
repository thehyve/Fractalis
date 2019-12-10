"""
Documentation: http://stackoverflow.com/questions/24238743/flask-decorator-to-verify-json-and-json-schema  # noqa: 501
"""
from functools import wraps

from flask import request, jsonify
from pydantic import BaseModel, ValidationError
from werkzeug.exceptions import BadRequest


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            json = request.get_json(force=True)
            if not (json):
                raise BadRequest()
        except BadRequest:
            error_msg = "Request payload must be valid JSON."
            return jsonify({'error': error_msg}), 400
        return f(*args, **kwargs)
    return wrapper


def validate_schema(schema_model: BaseModel):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            json = request.get_json(force=True)
            try:
                schema_model(**json)
            except ValidationError as e:
                return jsonify({'error': e.json()}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator
