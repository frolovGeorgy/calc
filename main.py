from fastapi import FastAPI

from db import CalculationHistory
from routers import calc

app = FastAPI()
history = CalculationHistory()
app.include_router(calc.router)
