from fastapi import APIRouter, UploadFile, File, HTTPException
from ...functions import IOUtils
import time
import json

router = APIRouter(redirect_slashes=False)
RESULT_DIR = IOUtils.create_dir("cache")


@router.post("/api/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    timestamp = int(time.time())
    config_name = f"config_{timestamp}"
    file_location = RESULT_DIR / f"{config_name}.json"

    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())

        config_info = {"name": config_name, "timestamp": timestamp}

        # use config_info.json to store index
        config_info_location = RESULT_DIR / "config_info.json"
        if config_info_location.exists():
            with open(config_info_location, "r") as f:
                config_data = json.load(f)
        else:
            config_data = []

        config_data.append(config_info)

        with open(config_info_location, "w") as f:
            json.dump(config_data, f)

        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
