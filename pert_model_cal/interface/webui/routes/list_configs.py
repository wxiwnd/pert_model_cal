from fastapi import APIRouter, Request, HTTPException
from ...functions import IOUtils

router = APIRouter(redirect_slashes=False)

RESULT_DIR = IOUtils.create_dir("cache")


@router.get("/api/list_configs")
async def list_configs():
    config_files = list(RESULT_DIR.glob("*.json"))
    config_list = [str(file.name) for file in config_files]
    return {"configs": config_list}


@router.post("/api/list_details")
async def list_details(request: Request):
    body = await request.json()
    config_name: str = body.get("config_name")
    if not config_name:
        raise HTTPException(status_code=400, detail="config_name is required")

    json_file = RESULT_DIR / f"{config_name}.json"
    csv_file_summary = RESULT_DIR / f"{config_name}_summary.csv"
    csv_file_tasks = RESULT_DIR / f"{config_name}_tasks.csv"
    excel_file_summary = RESULT_DIR / f"{config_name}_summary.xlsx"
    excel_file_tasks = RESULT_DIR / f"{config_name}_tasks.xlsx"

    if not json_file.exists():
        raise HTTPException(status_code=404, detail="JSON file not found")
    if not csv_file_summary.exists():
        raise HTTPException(status_code=404, detail="CSV summary file not found")
    if not csv_file_tasks.exists():
        raise HTTPException(status_code=404, detail="CSV tasks file not found")
    if not excel_file_summary.exists():
        raise HTTPException(status_code=404, detail="Excel summary file not found")
    if not excel_file_tasks.exists():
        raise HTTPException(status_code=404, detail="Excel tasks file not found")

    with open(json_file, "r") as f:
        json_content = f.read()

    with open(csv_file_summary, "r") as f:
        csv_summary_content = f.read()

    with open(csv_file_tasks, "r") as f:
        csv_tasks_content = f.read()

    return {
        "json_content": json_content,
        "csv_summary_content": csv_summary_content,
        "csv_tasks_content": csv_tasks_content,
    }
