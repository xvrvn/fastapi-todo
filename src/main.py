import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.auth.router import router as auth_router
from src.config import settings
from src.database import init_db
from src.exceptions import validation_exception_handler
from src.middlewares import disable_http_cache_middleware
from src.tasks.router import router as tasks_router


async def lifespan(app: FastAPI):
    await init_db()

    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    backend = RedisBackend(redis)
    FastAPICache.init(backend, prefix="fastapi-cache")
    yield
    await redis.close()


app = FastAPI(title="Todo API", version="0.2.0", lifespan=lifespan)  # type: ignore


app.middleware("http")(disable_http_cache_middleware)


app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])


@app.get("/")
async def root():
    return {"message": "Welcome to Todo API (async + cache)"}
