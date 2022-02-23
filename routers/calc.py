import operator
from typing import Dict, List, Callable, Union

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException

from db import history, Record

router = APIRouter()


@router.get(
    '/calc',
    response_description="Random phrase",
    description="Get random phrase from database",
)
async def calculate(
        expression: str = Query(
            ...,
            tite='Input expression',
            regex='^(?:[-+]\s*)?(?:[(]\s*)?(?:[-+]?\s*)?\d*[.]?\d*(?:\s*(?:[)])?(?:[-+*/])?(?:[(])?(?:\d*[.]?\d*)?)*$',
        )
):
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

    for token in expression.replace(' ', ''):
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

    except (ValueError, IndexError, KeyError, TypeError):
        history.add_record(Record(request=expression, response='', status='fail'))
        raise HTTPException(status_code=422, detail='Wrong expression')

    except ZeroDivisionError:
        history.add_record(Record(request=expression, response='', status='fail'))
        raise HTTPException(status_code=422, detail='Division by zero')

    history.add_record(Record(request=expression, response=str(stack[0]), status='success'))

    return {"response": round(stack[0], 3)}
