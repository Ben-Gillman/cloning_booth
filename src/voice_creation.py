from fastapi import APIRouter
import requests
from pathlib import Path

from src.file_management import sync_local_to_private_s3

router = APIRouter(responses={404: {"description": "Not found"}}, tags=["Voice"])

API_KEY = Path("/home/bgillman/secret/eleven_labs_api_key.txt").read_text().rstrip()


@router.get("/voice/", description="Return all the voices associated with the account")
async def get_voices():
    response = requests.get(
        url="https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": API_KEY}
    )
    return response.text


async def get_name_for_voice(voice_id: str) -> str:
    response = requests.get(
        url=f"https://api.elevenlabs.io/v1/voices/{voice_id}?with_settings=false",
        headers={"xi-api-key": API_KEY},
    )
    return response.json()["name"]


@router.post(
    "/voice/text_to_speech/{voice_id}",
    description="This will take an existing voice and new text and produce new audio as an mp3 file",
)
async def text_to_speach(voice_id: str):
    name = await get_name_for_voice(voice_id)

    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "voice/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": f"{API_KEY}",
    }

    data = {
        "text": Path("/home/bgillman/cloning_booth/ai_voice_intro.txt")
        .read_text()
        .rstrip(),
        "model_id": "eleven_monolingual_v1",  # This is their English model
        "voice_settings": {"stability": 0.4, "similarity_boost": 1},
    }
    print("Making call to 11labs")
    response = requests.post(url, json=data, headers=headers)

    print("Saving voice data")
    file_name = f"/home/bgillman/cloning_booth_media/{name}_voice_prompt.mp3"
    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    print("Pushing file to aws s3")
    sync_local_to_private_s3()


@router.post(
    "/voice/create/{participant_name}",
    description="This will create a new voice id given audio to clone from",
)
async def create_new_voice(participant_name: str) -> str:
    url = "https://api.elevenlabs.io/v1/voices/add"

    headers = {"Accept": "application/json", "xi-api-key": f"{API_KEY}"}

    data = {
        "name": f"{participant_name}",
        "labels": '{"accent": "American"}',
        "description": f"Voice of {participant_name}",
    }

    files = [
        (
            "files",
            (
                f"{participant_name}_input.m4a",
                open(
                    f"/home/bgillman/cloning_booth_media/{participant_name}_input.m4a",
                    "rb",
                ),
                "audio/mpeg",
            ),
        )
    ]

    response = requests.post(url, headers=headers, data=data, files=files)
    print(f"{response.text} has been created")
    return response.json().get("voice_id")
