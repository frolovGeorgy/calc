import operator
from typing import Dict, List, Callable, Union

from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError

from db import Calculator, history, Record

router = APIRouter()


@router.post(
    '/calc',
    response_description="Random phrase",
    description="Get random phrase from database",
)
async def calculate(calculator: Calculator):
    priority: Dict[str, List[Union[int, Callable, None]]] = {
        '(': [0, None],
        '+': [1, operator.add],
        '-': [1, operator.sub],
        '_': [1, operator.neg],
        '*': [2, operator.mul],
        '/': [2, operator.truediv]
    }
    # TODO check ZeroDivisionError
    exp_list = []
    last_token = ''

    for token in calculator.expression.replace(' ', ''):
        if token == '-':
            if not last_token:
                exp_list.append('_')

            else:
                exp_list.append(last_token)
                last_token = ''
                exp_list.append(token)

        elif token == '+':
            if last_token:
                exp_list.append(last_token)
                last_token = ''
                exp_list.append(token)

        elif token in '*/()':
            if last_token:
                exp_list.append(last_token)
                last_token = ''
            exp_list.append(token)

        else:
            last_token += token

    else:
        if last_token:
            exp_list.append(last_token)

    operators = []
    postfix = []
    stack = []

    try:
        for sym in exp_list:
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
            if elem == '_':
                stack.append(priority[elem][1](stack.pop()))

            elif elem in priority:
                stack.append(priority[elem][1](stack.pop(-2), stack.pop()))

            else:
                stack.append(float(elem))

    except (ValueError, IndexError, KeyError):
        history.add_record(Record(request=calculator.expression, response='', status='fail'))
        raise RequestValidationError

    history.add_record(Record(request=calculator.expression, response=str(stack[0]), status='success'))

    return {"response": round(stack[0], 3)}
