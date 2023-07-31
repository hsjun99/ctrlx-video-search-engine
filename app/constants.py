import os

import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


APP_TITLE = "ctrlx-video-search-engine"
APP_VERSION = "0.0.1"

RABBITMQ_SERVER = os.getenv("RABBITMQ_SERVER_DEVELOPMENT")
