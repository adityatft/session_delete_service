import os
import env_file

try:
    env_file.load(".env")
except Exception as err:
    pass

HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")
DEBUG_MODE = os.environ.get("DEBUG_MODE")

ROOT_URL = os.path.join(os.environ.get("BASE_URL"), os.environ.get("BACKEND_URL"))
ORG_NAME = os.environ.get("ORG_NAME")

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.environ.get("AWS_DEFAULT_REGION")
ECR_BROWSER_IMAGES = os.environ.get("AWS_ECR_IMAGE")
S3_BUCKET = os.environ.get("S3_BUCKET")


LOG_LEVEL = os.environ.get("LOG_LEVEL")
LOG_FORMAT = os.environ.get("LOG_FORMAT")
LOG_GROUP_NAME = os.environ.get("LOG_GROUP_NAME")


POD_DELETION_WAIT_TIME = int(os.environ.get("POD_WAIT_TIME"))
FUNC_RETRY_LIMIT = int(os.environ.get("RETRY_LIMIT"))
FUNC_RETRY_PAUSE_TIME = int(os.environ.get("RETRY_PAUSE_TIME"))

HEADERS = {
    "Content-Type": "application/json"
}
