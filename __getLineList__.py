from io import TextIOWrapper
from typing import overload

def getLineList(_file: TextIOWrapper, headerPrefix="! //", commentPrefix="!") -> ([str], [str]):
    headerLines = []
    lines: [str] = []

    while True:
        position = _file.tell()
        line = _file.readline()

        # We hit a header
        if (line.startswith(headerPrefix)):
            if len(headerLines) == 0:
                headerLines.append(line)
                continue
            _file.seek(position) # reset to 
            break

        # A non-header comment
        elif (line.startswith(commentPrefix)):
            if len(lines) == 0:
                headerLines.append(line) # Assume that the comment is extra description 
            else:
                lines.append(line)
            continue

        if (line == "\n"):
            # empty newlines aren't kept in the sorted files at the moment
            # prefer just writing an extra newline after each set of lines is written to the file
            continue 

        # We hit the end of the file
        if (line == ""):
            break

        lines.append(line)

    
    
    return (headerLines, lines)

@overload
def getSortedLineList(_lineList: ([str], [str])) -> [str]:
    ...

@overload
def getSortedLineList(_file: TextIOWrapper) -> [str]:
    ...

def getSortedLineList(_input, headerPrefix="! //", commentPrefix="!") -> [str]:
    headerlines = []
    lines = []
    if type(_input) is tuple:
        headerlines = _input[0]
        lines = _input[1]
    elif type(_input) is TextIOWrapper:
        headerLines, lines = getLineList(_file=_input, headerPrefix=headerPrefix, commentPrefix=commentPrefix)

    decorated = [(_line.removeprefix(commentPrefix).strip(" .").lower(), i, _line) for i, _line in enumerate(lines)]
    decorated.sort()
    sortedLines = [line for _line, i, line in decorated]

    return headerLines + sortedLines

