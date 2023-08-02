import os

import dotenv

from langchain.embeddings.openai import OpenAIEmbeddings

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


APP_TITLE = "ctrlx-video-search-engine"
APP_VERSION = "0.0.1"

RABBITMQ_SERVER = os.getenv("RABBITMQ_SERVER_DEVELOPMENT")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENV = os.environ["PINECONE_ENV"]

MIME_TYPES = {
    "video/mp4": "mp4",
    "video/quicktime": "mov",
    "video/x-matroska": "mkv",
    "video/webm": "webm",
    "video/x-msvideo": "avi",
    "video/ogg": "ogg",
    "video/x-flv": "flv",
    "video/x-ms-wmv": "wmv",
    "video/mpeg": "mpeg",
    "video/3gpp": "3gp",
    "video/3gpp2": "3g2",
    "video/x-m4v": "m4v",
    "video/x-flw": "flv",
    "application/x-mpegURL": "m3u8",
    "video/MP2T": "ts",
    "video/avi": "avi",
    "video/x-ms-asf": "asf",
}


FAISS_DIMENSION = 512

CLIP_DIMENSION = 512
OPENAI_DIMENSION = 768

OPENAI_EMBEDDING = OpenAIEmbeddings()

FRAME_VECTORSTORE_INDEX = "frame"
SCENE_VECTORSTORE_INDEX = "scene"
