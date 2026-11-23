from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import chat, forecast, health, intent, restock
from app.schemas import ErrorDetail, StandardErrorResponse


def verify_internal_key(x_internal_key: str | None = Header(default=None)) -> None:
    expected = settings.ai_service_internal_key.strip()
    if expected and x_internal_key != expected:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Header X-Internal-Key tidak valid atau tidak ditemukan."},
        )


app = FastAPI(
    title="Matchamind x Hidji AI & Forecast Service",
    version="1.0.0",
    description="Microservice FastAPI untuk klasifikasi intent NLP, forecasting kebutuhan bahan (Ridge DS), dan restock advisor.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        code = str(exc.detail.get("code", "HTTP_ERROR"))
        message = str(exc.detail.get("message", "Terjadi kesalahan pada permintaan."))
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)

    body = StandardErrorResponse(error=ErrorDetail(code=code, message=message, details=[]))
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    body = StandardErrorResponse(
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Format data permintaan tidak valid.",
            details=[{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()],
        )
    )
    return JSONResponse(status_code=422, content=body.model_dump())


app.include_router(health.router)
app.include_router(intent.router, dependencies=[Depends(verify_internal_key)])
app.include_router(forecast.router, dependencies=[Depends(verify_internal_key)])
app.include_router(restock.router, dependencies=[Depends(verify_internal_key)])
app.include_router(chat.router, dependencies=[Depends(verify_internal_key)])
