import random

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from settings import Settings

app = FastAPI()
settings = Settings()


@app.get("/health")
async def healthcheck():
    return {"status": "Ok"}


@app.get("/api/movies")
async def proxy_movies(request: Request):
    url = settings.monolith_url
    if (
        settings.gradual_migration
        and random.randint(1, 100) <= settings.movies_migration_percent
    ):
        url = settings.movies_service_url

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/api/movies",
            params=request.query_params,
            headers=request.headers,
            cookies=request.cookies,
        )
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/api/movies/health")
async def check_health_movies(request: Request):
    url = settings.movies_service_url

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/api/movies/health",
            params=request.query_params,
            headers=request.headers,
            cookies=request.cookies,
        )
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/api/users")
async def proxy_users(request: Request):
    url = settings.monolith_url

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/api/users",
            params=request.query_params,
            headers=request.headers,
            cookies=request.cookies,
        )
        return JSONResponse(status_code=response.status_code, content=response.json())


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
