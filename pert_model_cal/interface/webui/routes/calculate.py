from fastapi import APIRouter, Request, HTTPException
from ...functions import IOUtils

router = APIRouter(redirect_slashes=False)
RESULT_DIR = IOUtils.create_dir("cache")


@router.post("/api/calculate")
async def calculate(request: Request):
    body = await request.json()
    config_name: str = body.get("config_name")
    expected_time = body.get("expected_time")
    expected_time = int(expected_time) if expected_time else None
    if not config_name:
        raise HTTPException(status_code=400, detail="config_name is required")
    try:
        file_name = f"{config_name}.json"
        file_location = RESULT_DIR / file_name
        pert_result = IOUtils.calculate_pert(file_location, time=expected_time)
        IOUtils.generate_table(
            pert_result=pert_result,
            table_format=["csv", "excel"],
            save_path=RESULT_DIR,
            config_name=config_name,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
