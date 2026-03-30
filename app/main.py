import sys
from pathlib import Path

path_to_exam2 = Path(__file__).resolve().parent.parent
if str(path_to_exam2) not in sys.path:
    sys.path.insert(0, str(path_to_exam2))

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.api.routers.auth import auth_router  
from app.api.routers.categories import router
import time

app = FastAPI()

app.mount('/static', StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request {request.method} {request.url} processed in {process_time:.4f} seconds")
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

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

from app.api.routers.products import router as products_router
from app.api.routers.cart import router as cart_router
from app.api.routers.orders import router as orders_router
from app.api.routers.reviews import router as reviews_router
from app.api.routers.users import router as users_router

app.include_router(products_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")




if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8002, reload=True)