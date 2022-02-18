from typing import Optional

from pydantic import BaseModel, Field


class Calculator(BaseModel):
    expression: str = Field(
        ...,
        tite='Input expression',
        regex='^(?:[-+]\s)?(?:[(]\s)?(?:[-+]?\s?)?\d*[.]?\d*(?:\s(?:[)])?(?:[-+*/])?(?:[(])?(?:\d*[.]?\d*)?)*$',
    )


class CalculationHistory:

    def __init__(self):
        self.history = []

    def get(self, num: int = 30, status: Optional[str] = None):
        if status == 'success':
            result = [filter(lambda x: x['status'] == 'success', self.history[:30])]

        elif status == 'fail':
            result = [filter(lambda x: x['status'] == 'fail', self.history[:30])]

        else:
            result = self.history[:num]

        return result

    def add(self, request: str, response: str, status: str):
        if len(self.history) >= 30:
            self.history.pop(0)

        self.history.append(
            {
                'request': request,
                'response': response,
                'status': status
            }
        )
