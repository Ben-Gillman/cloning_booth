from fastapi import APIRouter
import requests
import os
from pathlib import Path
import time

from src.file_management import sync_private_to_public_s3, remove_all_public_s3
from src.voice_creation import create_new_voice, text_to_speach

router = APIRouter(responses={404: {"description": "Not found"}}, tags=["Video"])


API_KEY = Path("/home/bgillman/secret/d_id_api_key.txt").read_text().rstrip().split(":")
AUTH = requests.auth.HTTPBasicAuth(API_KEY[0], API_KEY[1])


@router.get(
    "/video/{video_id}",
    description="This gets a single video on my account",
)
async def get_video(video_id: str):
    "Example video id's: tlk_adPOqO3jesgZ6senvRW2M, tlk_gAL2ONo4baZ6vBdJKG7oW"
    response = requests.get(
        url=f"https://api.d-id.com/talks/{video_id}",
        auth=AUTH,
    )
    print(f"got for video response={response.text}")
    return response.json()["result_url"]


@router.get(
    "/video",
    description="This gets all the videos on my account",
)
async def get_videos():
    response = requests.get(
        url=f"https://api.d-id.com/talks",
        auth=AUTH,
    )
    print(response.text)
    return response.json()


@router.post("/video", description="Returns id of newly created video")
async def make_video(name: str) -> str:
    """
    Urls must be https and end in proper file extension
    Reference here: https://docs.d-id.com/reference/createtalk
    """

    sync_private_to_public_s3()

    voice_url = (
        f"https://cloningboothmediapublic.s3.amazonaws.com/{name}_voice_prompt.mp3"
    )
    img_url = f"https://cloningboothmediapublic.s3.amazonaws.com/{name}.jpg"

    response = requests.post(
        url=f"https://api.d-id.com/talks",
        auth=AUTH,
        json={
            "source_url": img_url,
            "script": {"type": "audio", "subtitles": False, "audio_url": voice_url},
            "persist": False,
        },
    )

    print(f"created video with response={response.text}")
    remove_all_public_s3()

    video_result_url: str = None
    while video_result_url is None:
        resp = await get_video(response.json()["id"])
        if resp["status"] == "done":
            video_result_url = resp["result_url"]
        else:
            print("video not ready, sleeping 5 seconds")
            time.sleep(5)

    return video_result_url


@router.get(
    "/video/end_to_end",
    description="Calls all necessary endpoints to create video, given participant name, "
    "assumes image and audio input files exist",
)
async def make_video_e2e(name: str) -> str:
    voice_id = create_new_voice(name)

    # Saves audio in s3 as <name_voice_prompt.mp3>
    text_to_speach(voice_id)

    result_url = make_video(name)

    return result_url
