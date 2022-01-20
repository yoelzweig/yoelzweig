# sudoku → japanese acronym (su, doku → number, single (+ gr. akros, onyma → edge, name); fr → us ("number place") → jp → ..)
# (= dos(denial-of-service)-attack on the brain (?))

# 9x9 grid with 9 3x3 subgrids; each subgrid, row, and column contains the numbers 1..9 once (+ unique solution)

from collections import deque

legal_entries = [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]

test_sudoku = [-1,4,-1,-1,-1,5,1,2,-1,-1,-1,-1,-1,1,-1,-1,-1,6,-1,-1,2,-1,-1,-1,-1,-1,8,-1,-1,-1,-1,-1,-1,6,-1,-1,9,-1,-1,-1,-1,8,-1,-1,-1,-1,-1,3,-1,9,-1,4,1,-1,-1,5,-1,7,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,2,-1,-1,4,-1,8,-1,9,3,-1]


class Sudoku:
    """
    # list of 81 entries from top-left to bottom-right (-1 → empty)
    """
    def __init__(self, entries):
        self.entries = entries[:]
        self.original_entries = entries[:]

    def __repr__(self):
        rows = ["sudoku:\n"]
        for row in range(9):
            current_row = []
            for column in range(9):
                current_row.append(str(self.entries[row * 9 + column]))
                if current_row[-1][0] != "-":
                    current_row[-1] = " " + current_row[-1]
            rows.append(" ".join(current_row) + "\n")
        return "".join(rows)

    def reset(self):
        self.entries = self.original_entries[:]

    def no_duplicates(self, indices):
        # True if all entries (not -1) pointed at by indices are different
        entries = [self.entries[index] for index in indices]
        for entry in range(1, 9 + 1):
            if entries.count(entry) > 1:
                return False
        return True

    def no_errors(self):
        # no illegal entries
        if not (len(self.entries) == 81 and all(entry in legal_entries for entry in self.entries)):
            return False
        # all subgrids correct
        for subgrid in range(9):
            indices = get_indices_from_subgrid(subgrid)
            if not self.no_duplicates(indices):
                return False
        # all rows correct
        for row in range(9):
            indices = get_indices_from_row(row)
            if not self.no_duplicates(indices):
                return False
        # all columns correct
        for column in range(9):
            indices = get_indices_from_column(column)
            if not self.no_duplicates(indices):
                return False
        return True

    def possible_entries_for_index(self, index):
        if self.entries[index] != -1:
            return [self.entries[index]]
        impossible_entries = set()
        subgrid = get_subgrid_from_index(index)
        row = get_row_from_index(index)
        column = get_column_from_index(index)
        for i in get_indices_from_subgrid(subgrid):
            impossible_entries.add(self.entries[i])
        for i in get_indices_from_row(row):
            impossible_entries.add(self.entries[i])
        for i in get_indices_from_column(column):
            impossible_entries.add(self.entries[i])
        possible_entries = []
        for entry in range(1, 9 + 1):
            if entry not in impossible_entries:
                possible_entries.append(entry)
        return possible_entries

    def solve_next_entry(self, quiet=False):
        # return 1 for new_entry, 0 for no_new_entry, -1 for error
        possible_entries_for_indices = []
        # index level
        for index in range(81):
            if self.entries[index] == -1:
                possible_entries = self.possible_entries_for_index(index)
                if len(possible_entries) == 1:  # success
                    if not quiet:
                        row = get_row_from_index(index)
                        column = get_column_from_index(index)
                        print(f"New entry at row {row}, column {column}: {possible_entries[0]} [index level]")
                    self.entries[index] = possible_entries[0]
                    return 1
                possible_entries_for_indices.append(possible_entries)
            else:
                possible_entries_for_indices.append([self.entries[index]])
        for index in range(81):
            if not len(possible_entries_for_indices[index]):  # error check
                if not quiet:
                    row = get_row_from_index(index)
                    column = get_column_from_index(index)
                    print(f"Error at row {row}, column {column}: no possible entries")
                return -1
        # subgrid level (mode 0) + row level (mode 1) + column level (mode 2)
        for mode in range(3):
            for i in range(9):
                indices = get_indices_for_mode(mode)(i)
                entries = set()
                for index in indices:
                    entries.add(self.entries[index])
                missing_entries = []
                for entry in range(1, 9 + 1):
                    if entry not in entries:
                        missing_entries.append(entry)
                for missing_entry in missing_entries:
                    count = 0
                    pos = -1
                    for index in indices:
                        if missing_entry in possible_entries_for_indices[index]:
                            count += 1
                            pos = index
                    if count == 1:  # success
                        if not quiet:
                            row = get_row_from_index(pos)
                            column = get_column_from_index(pos)
                            print(f"New entry at row {row}, column {column}: {missing_entry} [{'subgrid' if mode == 0 else 'row' if mode == 1 else 'column'} level]")
                        self.entries[pos] = missing_entry
                        return 1
                    elif not count:  # error check
                        if not quiet:
                            print(f"Error at {'subgrid' if mode == 0 else 'row' if mode == 1 else 'column'} {i}: no place for '{missing_entry}'")
                        return -1
        # ...
        return 0

    def solve(self):
        dq = deque()
        dq.append(self.entries[:])
        while len(dq):
            dq_entries = dq.pop()
            self.entries = dq_entries
            while True:
                flag = self.solve_next_entry(quiet=True)
                if flag == 1:  # new_entry
                    continue
                elif flag == 0:  # no new entry
                    if all(entry in legal_entries[1:] for entry in self.entries):  # terminated?
                        dq.clear()
                        break
                    else:  # depth first search
                        for index in range(81):
                            if self.entries[index] == -1:
                                possible_entries = self.possible_entries_for_index(index)
                                for entry in possible_entries:
                                    self.entries[index] = entry
                                    dq.append(self.entries[:])  # [:] !
                                break
                else:  # flag == -1, error
                    break
        assert self.no_errors()
        if all(entry in legal_entries[1:] for entry in self.entries):
            print("\nSudoku solved.", end="\n\n")
            print(self)
        else:
            print("\nSudoku not solved.", end="\n\n")
            print(self)


def get_subgrid_from_index(index):
    # top-left to bottom-right, 0-based
    row = get_row_from_index(index)
    column = get_column_from_index(index)
    return 3 * (row // 3) + column // 3


def get_row_from_index(index):
    # 0-based
    return index // 9


def get_column_from_index(index):
    # 0-based
    return index % 9


def get_indices_from_subgrid(subgrid):
    # 0-based
    r = (subgrid // 3) * 3
    c = (subgrid % 3) * 3
    indices = []
    for row in range(r, r + 3):
        for column in range(c, c + 3):
            indices.append(row * 9 + column)
    return indices


def get_indices_from_row(row):
    # 0-based
    return list(range(row * 9, row * 9 + 9))


def get_indices_from_column(column):
    # 0-based
    return list(range(column, column + 8 * 9 + 1, 9))


def get_indices_for_mode(mode):
    if mode == 0:
        return get_indices_from_subgrid
    elif mode == 1:
        return get_indices_from_row
    else:
        return get_indices_from_column


def print_entries(entries):
    # quick & dirty
    print("-" * 10)
    for row in range(9):
        print(*entries[row * 9:row * 9 + 9])
    print("-" * 10)


if __name__ == "__main__":
    print("Enter the sudoku row by row (top to bottom, -1 → empty):", end="\n\n")
    sudoku_entries = []
    for my_row in range(9):
        my_row_entries = input(f"Enter the row {my_row} entries as a comma separated tuple:\n")
        sudoku_entries.extend([int(entry) for entry in my_row_entries.split(",")])
    sudoku = Sudoku(sudoku_entries)
    print("\nPlease verify your starting entries:")
    print(sudoku)
    while True:
        answer = input("Do you want to make a correction? ('yes'/'no')\n")
        if answer.lower() in ["yes", "'yes'", '"yes"', "y"]:
            correction = input("Enter the row, column, and corrected entry as a comma separated tuple (0-based):\n")
            correction = [int(entry) for entry in correction.split(",")]
            sudoku.entries[(correction[0]) * 9 + (correction[1])] = correction[2]
            print("\n", sudoku, sep="")
        else:
            if not sudoku.no_errors():
                print("\nPlease verify your entries again:")
                print(sudoku)
            else:
                break
    sudoku.solve()
