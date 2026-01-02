import copy

# ======================================================
# CONFIG
# ======================================================

BUREAUCRAT_STARTS = {(1, 4), (6, 4)}  # starting squares only

# ======================================================
# BOARD
# ======================================================

def initial_board():
    return [
        ["r","n","b","q","k","b","n","r"],
        ["p","p","p","p","c","p","p","p"],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        ["P","P","P","P","C","P","P","P"],
        ["R","N","B","Q","K","B","N","R"]
    ]

# ======================================================
# HELPERS
# ======================================================

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def is_white(p):
    return p.isupper()

def enemy(p1, p2):
    return p2 != "." and is_white(p1) != is_white(p2)

# ======================================================
# PSEUDO-LEGAL MOVE GENERATORS
# ======================================================

def rook_moves(board, r, c):
    return sliding(board, r, c, [(1,0),(-1,0),(0,1),(0,-1)])

def bishop_moves(board, r, c):
    return sliding(board, r, c, [(1,1),(1,-1),(-1,1),(-1,-1)])

def queen_moves(board, r, c):
    return rook_moves(board, r, c) + bishop_moves(board, r, c)

def sliding(board, r, c, directions):
    moves = []
    p = board[r][c]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] == ".":
                moves.append((nr, nc))
            elif enemy(p, board[nr][nc]):
                moves.append((nr, nc))
                break
            else:
                break
            nr += dr
            nc += dc
    return moves

def knight_moves(board, r, c):
    moves = []
    p = board[r][c]

    for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and (board[nr][nc] == "." or enemy(p, board[nr][nc])):
            moves.append((nr, nc))
    return moves

def king_moves(board, r, c):
    moves = []
    p = board[r][c]

    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr == dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and (board[nr][nc] == "." or enemy(p, board[nr][nc])):
                moves.append((nr, nc))
    return moves

def pawn_moves(board, r, c):
    moves = []
    p = board[r][c]

    direction = -1 if is_white(p) else 1
    start_row = 6 if is_white(p) else 1

    # Forward move
    if in_bounds(r + direction, c) and board[r + direction][c] == ".":
        moves.append((r + direction, c))
        if r == start_row and board[r + 2 * direction][c] == ".":
            moves.append((r + 2 * direction, c))

    # Captures
    for dc in (-1, 1):
        nr, nc = r + direction, c + dc
        if in_bounds(nr, nc) and enemy(p, board[nr][nc]):
            moves.append((nr, nc))

    return moves

def bureaucrat_moves(board, r, c):
    # Any empty square, no captures
    return [(rr, cc) for rr in range(8) for cc in range(8) if board[rr][cc] == "."]

# ======================================================
# MOVE DISPATCH
# ======================================================

def pseudo_legal_moves(board, r, c):
    p = board[r][c]
    if p == ".":
        return []

    # Bureaucrat (only if from starting square)
    if p.lower() == "c":
        return bureaucrat_moves(board, r, c)

    if p.lower() == "r":
        return rook_moves(board, r, c)
    if p.lower() == "b":
        return bishop_moves(board, r, c)
    if p.lower() == "q":
        return queen_moves(board, r, c)
    if p.lower() == "n":
        return knight_moves(board, r, c)
    if p.lower() == "k":
        return king_moves(board, r, c)
    if p.lower() == "p":
        return pawn_moves(board, r, c)

    return []

# ======================================================
# CHECK LOGIC
# ======================================================

def find_king(board, color):
    target = "K" if color == "white" else "k"
    for r in range(8):
        for c in range(8):
            if board[r][c] == target:
                return r, c
    return None

def is_in_check(board, color):
    king_pos = find_king(board, color)
    if not king_pos:
        return False

    kr, kc = king_pos

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == "." or is_white(p) == (color == "white"):
                continue

            # Bureaucrat does not give check
            if p.lower() == "b" and (r, c) in BUREAUCRAT_STARTS:
                continue

            if (kr, kc) in pseudo_legal_moves(board, r, c):
                return True

    return False

# ======================================================
# LEGAL MOVE FILTER
# ======================================================

def legal_moves(board, r, c, turn):
    piece = board[r][c]
    if piece == ".":
        return []

    if is_white(piece) != (turn == "white"):
        return []

    legal = []

    for er, ec in pseudo_legal_moves(board, r, c):

        # Bureaucrat cannot capture
        if piece.lower() == "b" and (r, c) in BUREAUCRAT_STARTS:
            if board[er][ec] != ".":
                continue

        temp = copy.deepcopy(board)
        temp[er][ec] = temp[r][c]
        temp[r][c] = "."

        if not is_in_check(temp, turn):
            legal.append((er, ec))

    return legal

# ======================================================
# APPLY MOVE
# ======================================================

def apply_move(board, sr, sc, er, ec, turn):
    if (er, ec) not in legal_moves(board, sr, sc, turn):
        return board, False

    new_board = copy.deepcopy(board)
    new_board[er][ec] = new_board[sr][sc]
    new_board[sr][sc] = "."

    return new_board, True
