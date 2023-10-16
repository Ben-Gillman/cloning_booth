from fastapi import FastAPI
from fastapi import APIRouter
import uvicorn

from src.video_creation import router as video_creation_router
from src.voice_creation import router as voice_creation_router

app = FastAPI()

router = APIRouter()
router.include_router(video_creation_router)
router.include_router(voice_creation_router)


@app.get("/")
async def healthcheck():
    return {"message": "healthy"}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
    print("running")
