import random
from typing import Optional, List, Tuple, Dict

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


class TicTacGame:
    _new_potential_move: Tuple[Tuple[int, int]] = (
        (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1),
    )
    _tokens = ('X', 'O')
    _win = False

    def __init__(self, field: List[List[Optional[str]]], win_condition: int):
        self._field: List[List[Optional[str]]] = field
        self._col: int = len(field[0])
        self._row: int = len(field)
        self._win_condition: int = win_condition
        if self._win_condition > max(self._col, self._row):
            raise ValueError('Win condition is too small. Please increase field size or decrease win condition.')

        self._moves: int = 0
        self._tuns_history = {}
        self._nought_potential_moves: List[Tuple[int, int]] = []
        self._crosses_potential_moves: List[Tuple[int, int]] = []
        self._cells_values = {}

    def __str__(self):
        temp_field = ''
        col_width = []
        for col in range(self._col):
            columns = [self._field[row][col] for row in range(self._row)]
            col_width.append(len(max(columns, key=len)))

        for i, row in enumerate(range(self._row)):
            result = []
            for col in range(self._col):
                item = self._field[row][col].rjust(col_width[col])
                result.append(item)

            temp_field += ' | '.join(result)
            temp_field += '\n'

        return temp_field

    def start_game(self):
        while (not self._win) and self._moves < (self._col * self._row):
            self._make_turn()

        if self._win:
            self._tuns_history['result'] = 'Crosses won' if self._moves % 2 == 0 else 'Noughts won'
        else:
            self._tuns_history['result'] = 'Draw'

        return self._tuns_history

    def _make_turn(self):
        if self._moves == 0:
            turn = (round(self._row / 2) - 1, round(self._col / 2) - 1)
            self._field[turn[0]][turn[1]] = 'X'
            self._add_potential_moves(self._crosses_potential_moves, turn)

        elif self._moves % 2 == 1:
            turn = self._get_importance_values()
            self._field[turn[0]][turn[1]] = 'O'
            self._add_potential_moves(self._nought_potential_moves, turn)

        elif self._moves % 2 == 0:
            turn = self._get_importance_values()
            self._field[turn[0]][turn[1]] = 'X'
            self._add_potential_moves(self._crosses_potential_moves, turn)

        self._moves += 1

        self._save_turn()

    def _save_turn(self):
        self._tuns_history[f'Turn: {self._moves}'] = str(self)

    def _add_potential_moves(self, potential_moves: List[Tuple[int, int]], last_turn: Tuple[int, int]):
        for move in self._new_potential_move:
            if (self._col - 1) >= move[1] + last_turn[1] >= 0 and (self._row - 1) >= move[0] + last_turn[0] >= 0 \
                    and self._field[move[0] + last_turn[0]][move[1] + last_turn[1]] == ' ':

                new_move: Tuple[int, int] = ((move[0] + last_turn[0]), (move[1] + last_turn[1]))

                if new_move not in potential_moves:
                    potential_moves.append(new_move)

        if last_turn in self._nought_potential_moves:
            self._nought_potential_moves.remove(last_turn)
        if last_turn in self._crosses_potential_moves:
            self._crosses_potential_moves.remove(last_turn)

    def _get_importance_values(self):
        self.cells_values = {
            'defence': {},
            'attack': {}
        }

        attack = True if self._moves % 2 == 1 else False
        for move in self._nought_potential_moves:
            self._improve_cell_value(move, attack)

        attack = False if self._moves % 2 == 1 else True
        for move in self._crosses_potential_moves:
            self._improve_cell_value(move, attack)

        cells_values = {}

        for cell, value in self.cells_values['defence'].items():
            if cell in cells_values:
                cells_values[cell] += value
            else:
                cells_values[cell] = value

        for cell, value in self.cells_values['attack'].items():
            if cell in cells_values:
                cells_values[cell] += value
            else:
                cells_values[cell] = value

            if value == (self._win_condition - 1) ** 2:
                self._win = True
                return cell

        max_value = -1
        curr_cell = None
        cells_list = []
        for cell in cells_values:
            if cells_values[cell] > max_value:
                max_value = cells_values[cell]
                curr_cell = cell
                cells_list = [cell]
            elif cells_values[cell] == max_value:
                if self.cells_values['defence'].get(cell, 0) > self.cells_values['defence'].get(curr_cell, 0):
                    curr_cell = cell
                    cells_list = []
                cells_list.append(cell)

        return random.choice(cells_list)

    def _improve_cell_value(self, move: Tuple[int, int], attack: bool):
        self.cells_values['attack' if attack else 'defence'][move] = 0

        self.cells_values['attack' if attack else 'defence'][move] += \
            self._get_vertical_line(move, attack)

        self.cells_values['attack' if attack else 'defence'][move] += \
            self._get_horizontal_line(move, attack)

        self.cells_values['attack' if attack else 'defence'][move] += \
            self._get_first_diagonal_line(move, attack)

        self.cells_values['attack' if attack else 'defence'][move] += \
            self._get_second_diagonal_line(move, attack)

    def _get_vertical_line(self, move: Tuple[int, int], attack: bool):
        count = 0
        line_range = range(-self._win_condition + 1, self._win_condition)
        enemy_mark = self._tokens[(self._moves + 1) % 2]
        own_mark = self._tokens[self._moves % 2]

        for num in line_range:
            if attack and num != 0 and self._row - 1 >= move[0] + num >= 0:
                if self._field[move[0] + num][move[1]] == enemy_mark and num < 0:
                    count = 0
                elif self._field[move[0] + num][move[1]] == enemy_mark and num > 0:
                    break
                elif self._field[move[0] + num][move[1]] != ' ':
                    count += 1

            elif not attack and num != 0 and self._row - 1 >= move[0] + num >= 0:
                if self._field[move[0] + num][move[1]] == own_mark and num < 0:
                    count = 0
                elif self._field[move[0] + num][move[1]] == own_mark and num > 0:
                    break
                elif self._field[move[0] + num][move[1]] != ' ':
                    count += 1

        if attack:
            line_value = count ** 2
        else:
            line_value = count ** 3

        return line_value

    def _get_horizontal_line(self, move: Tuple[int, int], attack: bool):
        count = 0
        line_range = range(-self._win_condition + 1, self._win_condition)
        enemy_mark = self._tokens[(self._moves + 1) % 2]
        own_mark = self._tokens[self._moves % 2]

        for num in line_range:
            if attack and num != 0 and self._col - 1 >= move[1] + num >= 0:
                if self._field[move[0]][move[1] + num] == enemy_mark and num < 0:
                    count = 0
                elif self._field[move[0]][move[1] + num] == enemy_mark and num > 0:
                    break
                elif self._field[move[0]][move[1] + num] != ' ':
                    count += 1

            elif not attack and num != 0 and self._col - 1 >= move[1] + num >= 0:
                if self._field[move[0]][move[1] + num] == own_mark and num < 0:
                    count = 0
                elif self._field[move[0]][move[1] + num] == own_mark and num > 0:
                    break
                elif self._field[move[0]][move[1] + num] != ' ':
                    count += 1

        if attack:
            line_value = count ** 2
        else:
            line_value = count ** 3

        return line_value

    def _get_first_diagonal_line(self, move: Tuple[int, int], attack: bool):
        """diagonal like that '\'"""
        count = 0
        line_range = range(-self._win_condition + 1, self._win_condition)
        enemy_mark = self._tokens[(self._moves + 1) % 2]
        own_mark = self._tokens[self._moves % 2]

        for num in line_range:
            if attack and num != 0 and self._row - 1 >= move[0] + num >= 0 and self._col - 1 >= move[1] + num >= 0:
                if self._field[move[0] + num][move[1] + num] == enemy_mark and num < 0:
                    count = 0
                elif self._field[move[0] + num][move[1] + num] == enemy_mark and num > 0:
                    break
                elif self._field[move[0] + num][move[1] + num] != ' ':
                    count += 1

            elif not attack and num != 0 and self._row - 1 >= move[0] + num >= 0 and self._col - 1 >= move[1] + num >= 0:
                if self._field[move[0] + num][move[1] + num] == own_mark and num < 0:
                    count = 0
                elif self._field[move[0] + num][move[1] + num] == own_mark and num > 0:
                    break
                elif self._field[move[0] + num][move[1] + num] != ' ':
                    count += 1

        if attack:
            line_value = count ** 2
        else:
            line_value = count ** 3

        return line_value

    def _get_second_diagonal_line(self, move: Tuple[int, int], attack: bool):
        """diagonal like that '/'"""
        count = 0
        line_range = range(-self._win_condition + 1, self._win_condition)
        enemy_mark = self._tokens[(self._moves + 1) % 2]
        own_mark = self._tokens[self._moves % 2]

        for num in line_range:
            if attack and num != 0 and self._row - 1 >= move[0] - num >= 0 and self._col - 1 >= move[1] + num >= 0:
                if self._field[move[0] - num][move[1] + num] == enemy_mark and num < 0:
                    count = 0
                elif self._field[move[0] - num][move[1] + num] == enemy_mark and num > 0:
                    break
                elif self._field[move[0] - num][move[1] + num] != ' ':
                    count += 1

            elif not attack and num != 0 and self._row - 1 >= move[0] - num >= 0 and self._col - 1 >= move[1] + num >= 0:
                if self._field[move[0] - num][move[1] + num] == own_mark and num < 0:
                    count = 0
                elif self._field[move[0] - num][move[1] + num] == own_mark and num > 0:
                    break
                elif self._field[move[0] - num][move[1] + num] != ' ':
                    count += 1

        if attack:
            line_value = count ** 2
        else:
            line_value = count ** 3

        return line_value

    def _add_cells_value(self, line_value: Dict[Tuple[int, int], int], attack: bool):
        turn_type = 'attack' if attack else 'defence'
        for cell in line_value:
            if cell in self.cells_values:
                self.cells_values[turn_type][cell] += line_value[cell]
            else:
                self.cells_values[turn_type][cell] = line_value[cell]
