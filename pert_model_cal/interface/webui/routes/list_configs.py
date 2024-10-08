from fastapi import APIRouter, HTTPException, Request
from ...functions import IOUtils
import json

router = APIRouter(redirect_slashes=False)
RESULT_DIR = IOUtils.create_dir("cache")


@router.get("/api/list_configs")
async def list_configs():
    config_info_location = RESULT_DIR / "config_info.json"

    try:
        if config_info_location.exists():
            with open(config_info_location, "r") as f:
                config_data = json.load(f)
            return {"configs": config_data}
        else:
            return {"configs": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/list_details")
async def list_details(request: Request):
    body = await request.json()
    config_name: str = body.get("config_name")
    if not config_name:
        raise HTTPException(status_code=400, detail="config_name is required")

    json_file = RESULT_DIR / f"{config_name}.json"
    csv_file_summary = RESULT_DIR / f"{config_name}_summary.csv"
    csv_file_tasks = RESULT_DIR / f"{config_name}_tasks.csv"
    svg_graph_file = RESULT_DIR / f"{config_name}_graph.svg"

    if json_file.exists():
        with open(json_file, "r") as f:
            json_content = f.read()
    else:
        json_content = None

    if csv_file_tasks.exists():
        with open(csv_file_tasks, "r") as f:
            csv_tasks_content = f.read()
    else:
        csv_tasks_content = None

    if csv_file_summary.exists():
        with open(csv_file_summary, "r") as f:
            csv_summary_content = f.read()
    else:
        csv_summary_content = None

    if svg_graph_file.exists():
        with open(svg_graph_file, "r") as f:
            svg_graph_content = f.read()
    else:
        svg_graph_content = None

    return {
        "json_content": json_content,
        "csv_summary_content": csv_summary_content,
        "csv_tasks_content": csv_tasks_content,
        "svg_graph_content": svg_graph_content,
    }
