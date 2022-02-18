from typing import Optional

from fastapi import FastAPI, Request, status, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from db import history, Record
from routers import calc

app = FastAPI()
app.include_router(calc.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url == 'http://127.0.0.1:8000/calc':
        history.add_record(Record(request=exc.body['expression'], response='', status='fail'))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.args[0]}),
    )


@app.get('/history')
async def calculation_history(
        num: int = Query(
            30,
            description='Number of records. Default value is 30. It can be in range from 1 to 30.',
            ge=1,
            le=30,
        ),
        record_status: Optional[str] = Query(
            None,
            description='With what status to display records. Default value is "None". It can be "success" or "fail".',
        )
):
    return {'history': history.get_history(num, record_status)}
