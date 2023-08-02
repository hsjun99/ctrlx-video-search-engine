import os

import dotenv

from langchain.embeddings.openai import OpenAIEmbeddings

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


APP_TITLE = "ctrlx-video-search-engine"
APP_VERSION = "0.0.1"

RABBITMQ_SERVER = os.getenv("RABBITMQ_SERVER_DEVELOPMENT")

FAISS_DIMENSION = 512

OPENAI_EMBEDDING = OpenAIEmbeddings()
