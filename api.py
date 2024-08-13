from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from downloader.main import download


class Payload(BaseModel):
    url: str
    audioOnly: bool


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/download")
def post_download(payload: Payload) -> Payload:
    download(payload.url, payload.audioOnly)

    return payload


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
