from fastapi import FastAPI
from .interface.webui.routes.upload_file import router as file_upload_router

app = FastAPI()
app.include_router(file_upload_router)
