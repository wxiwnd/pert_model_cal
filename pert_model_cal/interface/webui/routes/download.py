from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ...functions import IOUtils
import os
from pathlib import Path

router = APIRouter(redirect_slashes=False)
RESULT_DIR = IOUtils.create_dir("cache")


@router.get("/api/download/{file_type}/{config_name}")
async def download_file(config_name: str, file_type: str):
    if file_type not in ["xlsx", "csv"]:
        raise HTTPException(status_code=400, detail="File Type Not Allowed")

    file_path = Path(RESULT_DIR) / f"{config_name}.{file_type}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=f"{config_name}.{file_type}",
    )
