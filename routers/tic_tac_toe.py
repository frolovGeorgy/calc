from fastapi import APIRouter, Query, HTTPException

from db import TicTacGame

router = APIRouter()


@router.get('/tic-tac-toe')
async def tic_tac_toe(
        field_size: str = Query(
            '3*3',
            description='Field size. Format: columns*rows',
            regex='^\d+\*\d+$'
        ), win_condition: int = Query(
            3,
            description='How many characters must be placed in a row to win'
        )
):
    col, row = field_size.split('*')
    if int(col) < 3 or int(row) < 3:
        raise HTTPException(status_code=422, detail='Field must be at least 3 by 3')

    field = [[' ' for _ in range(int(col))] for _ in range(int(row))]
    game = TicTacGame(field, win_condition)
    result = game.start_game()
    return result
