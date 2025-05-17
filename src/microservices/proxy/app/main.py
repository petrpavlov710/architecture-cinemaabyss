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


@app.api_route("/api/movies", methods=["GET", "POST"])
async def proxy_movies(request: Request):
    url = settings.monolith_url
    if (
        settings.gradual_migration
        and random.randint(1, 100) <= settings.movies_migration_percent
    ):
        url = settings.movies_service_url

    async with httpx.AsyncClient() as client:
        method = request.method.lower()

        request_kwargs = {
            "headers": dict(request.headers),
            "cookies": dict(request.cookies),
            "params": dict(request.query_params),
        }

        if method == "post":
            request_body = await request.body()
            if request_body:
                request_kwargs["content"] = request_body
                # Или, если ожидается JSON:
                # request_kwargs["json"] = await request.json()
        
        response = await client.request(
            method,
            f"{url}/api/movies",
            **request_kwargs
        )
        
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
        )


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


@app.api_route("/api/users", methods=["GET", "POST"])
async def proxy_users(request: Request):
    url = settings.monolith_url

    async with httpx.AsyncClient() as client:
        method = request.method.lower()

        request_kwargs = {
            "headers": dict(request.headers),
            "cookies": dict(request.cookies),
            "params": dict(request.query_params),
        }

        if method == "post":
            request_body = await request.body()
            if request_body:
                request_kwargs["content"] = request_body
        
        response = await client.request(
            method,
            f"{url}/api/users",
            **request_kwargs
        )
        
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
        )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
