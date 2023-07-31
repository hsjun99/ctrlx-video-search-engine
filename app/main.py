from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.constants import APP_TITLE, APP_VERSION

from app.routers import VideoRouter


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
)

origins = [
    "http://localhost:3000",
    # "https://www.agentify.ai",
    # "https://agentify-ai.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    VideoRouter
    # dependencies=[Depends(is_valid_access_token)],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080, reload=True, debug=True)
