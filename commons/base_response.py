from http import HTTPStatus
from flask import jsonify


class BaseResponse:
    def __init__(self, status_code=HTTPStatus.OK, msg="Successful", data=None):
        if data is None:
            data = {}
        self.status_code = status_code
        self.msg = msg
        self.data = data

    def send_response(self):
        return jsonify(status=self.status_code, data=self.data, msg=self.msg)
