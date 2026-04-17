def get_line_column(source: str, position: int) -> tuple[int, int]:
    if not source or position <= 0:
        return 1, 1

    line = 1
    column = 1
    limit = min(position, len(source))

    i = 0
    while i < limit:
        c = source[i]
        if c == "\r":
            if i + 1 < len(source) and source[i + 1] == "\n":
                i += 1
            line += 1
            column = 1
        elif c == "\n":
            line += 1
            column = 1
        else:
            column += 1
        i += 1

    return line, column
