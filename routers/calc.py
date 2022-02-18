import operator
from typing import Dict, List, Callable, Union

from fastapi import APIRouter, HTTPException

from db import Calculator

router = APIRouter()


@router.post('/calc')
async def calculate(calculator: Calculator):
    priority: Dict[str, List[Union[int, Callable, None]]] = {
        '(': [0, None],
        '+': [1, operator.add],
        '-': [1, operator.sub],
        '*': [2, operator.mul],
        '/': [2, operator.truediv]
    }

    exp = calculator.expression.split()
    operators = []
    postfix = []
    stack = []

    try:
        for sym in exp:
            if sym.lstrip('-').replace('.', '').isdigit():
                postfix.append(sym)

            elif sym == '(':
                operators.append(sym)

            elif sym == ')':
                last_operator = operators.pop()
                while last_operator != '(':
                    postfix.append(last_operator)
                    last_operator = operators.pop()

            else:
                while operators and priority[sym][0] <= priority[operators[-1]][0]:
                    postfix.append(operators.pop())
                operators.append(sym)

        while operators:
            postfix.append(operators.pop())

        for elem in postfix:
            if elem in priority and len(stack) >= 2:
                stack.append(priority[elem][1](stack.pop(-2), stack.pop()))
            elif elem == '-' and len(stack) == 1:
                stack.append(-stack.pop())
            else:
                stack.append(float(elem))

    except (ValueError, IndexError, KeyError):
        raise HTTPException(status_code=422, detail='Wrong expression please correct it and try again')

    return {"result": stack[0]}
