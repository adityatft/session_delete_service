import watchtower
import logging

from flask_cors import CORS
from flask import Flask

from api.session_delete_api import session_blueprint
from commons.env_info import HOST, PORT, ORG_NAME, LOG_LEVEL, LOG_GROUP_NAME, LOG_FORMAT

app = Flask(__name__)
CORS(app)


logging.basicConfig(level=LOG_LEVEL)
handler = watchtower.CloudWatchLogHandler(log_group_name=LOG_GROUP_NAME, log_stream_name=ORG_NAME)
handler.setFormatter(
    logging.Formatter(fmt=LOG_FORMAT))
app.logger.addHandler(handler)


app.register_blueprint(session_blueprint)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
