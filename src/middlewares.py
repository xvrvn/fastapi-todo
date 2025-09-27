from fastapi import Request, Response


async def disable_http_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    if "etag" in response.headers:
        del response.headers["etag"]
    return response
