from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .interface.webui.routes.upload_file import router as file_upload_router
from .interface.webui.routes.list_configs import router as list_config_router
from .interface.webui.routes.calculate import router as calculate_router
from .interface.webui.routes.download import router as download_router

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory="pert_model_cal/interface/webui/static"),
    name="static",
)

templates = Jinja2Templates(directory="pert_model_cal/interface/webui/templates")

app.include_router(file_upload_router)
app.include_router(list_config_router)
app.include_router(calculate_router)
app.include_router(download_router)


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
