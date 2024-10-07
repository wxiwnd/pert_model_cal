from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
from datetime import datetime
import shutil

from ...functions import IOUtils

router = APIRouter(redirect_slashes=False)

RESULT_DIR = IOUtils.create_dir("cache")


@router.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    file_extension = Path(file.filename).suffix

    if file_extension.lower() != ".json":
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{timestamp}{file_extension}"

    file_location = RESULT_DIR / file_name

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"info": "file saved successfully"}
