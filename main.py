import watchtower
import logging

from flask_cors import CORS
from flask import Flask
from flask_log_request_id import RequestID, RequestIDLogFilter

from api.session_delete_api import session_blueprint
from commons.env_info import HOST, PORT, DEBUG_MODE, ORG_NAME, LOG_LEVEL, LOG_GROUP_NAME, LOG_FORMAT,\
    ENABLE_CLOUDWATCH_LOGGING

app = Flask(__name__)
RequestID(app=app)
CORS(app)


logging.basicConfig(level=LOG_LEVEL)
if ENABLE_CLOUDWATCH_LOGGING:
    handler = watchtower.CloudWatchLogHandler(log_group_name=LOG_GROUP_NAME, log_stream_name=ORG_NAME)
    handler.addFilter(RequestIDLogFilter())
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT))
    app.logger.addHandler(handler)


app.register_blueprint(session_blueprint)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE)
