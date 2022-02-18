from typing import Optional, List

from pydantic import BaseModel, Field


class Calculator(BaseModel):
    expression: str = Field(
        ...,
        tite='Input expression',
        regex='^(?:[-+]\s*)?(?:[(]\s*)?(?:[-+]?\s*)?\d*[.]?\d*(?:\s*(?:[)])?(?:[-+*/])?(?:[(])?(?:\d*[.]?\d*)?)*$',
    )


class Record:
    request: str = Field(..., description='Client request')
    response: str = Field(..., description='Server response')
    status: str = Field(..., description='Response\'s status')

    def __init__(self, request, response, status):
        self.request = request
        self.response = response
        self.status = status


class RecordsHistory:

    def __init__(self):
        self.history: List[Record] = []

    def get_history(self, num: int = 30, status: Optional[str] = None):
        if status == 'success':
            result = list(filter(lambda x: x.status == 'success', self.history[:num]))

        elif status == 'fail':
            result = list(filter(lambda x: x.status == 'fail', self.history[:num]))

        elif status is None:
            result = self.history[:num]

        else:
            raise ValueError('Status can be only success, fail or None')

        return result

    def add_record(self, record: Record):
        if len(self.history) >= 30:
            self.history.pop(0)

        self.history.append(record)


history = RecordsHistory()
