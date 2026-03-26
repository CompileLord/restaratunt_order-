import sys
from pathlib import Path

path_to_exam2 = Path(__file__).resolve().parent.parent
if str(path_to_exam2) not in sys.path:
    sys.path.insert(0, str(path_to_exam2))

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routers.auth import auth_router  
from app.api.routers.categories import router

app = FastAPI()

app.mount('/static', StaticFiles(directory="static"), name="static")

app.include_router(
    auth_router,
    prefix="/api/v1",
    tags=["User"]
)

app.include_router(
    router=router,
    prefix="/api/v1",
    tags=["Category"]
)




if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)