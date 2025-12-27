from io import TextIOWrapper
from typing import overload

def getLineList(file: TextIOWrapper, headerPrefix="! //", commentPrefix="!") -> (list[str], list[str]):
    headerLines = []
    lines: list[str] = []

    while True:
        position = file.tell()
        line = file.readline()

        # We hit a header
        if (line.startswith(headerPrefix)):
            if len(headerLines) == 0:
                headerLines.append(line)
                continue
            file.seek(position) # reset to before the next header
            break

        # A non-header comment
        elif (line.startswith(commentPrefix)):
            if len(lines) == 0:
                headerLines.append(line) # Assume that the comment is extra description 
            else:
                lines.append(line)
            continue

        if (line == "\n"):
            if len(lines) == 0:
                headerLines.append(line)
            # empty newlines aren't kept in the sorted lines under the header
            continue 

        # We hit the end of the file
        if (line == ""):
            break

        lines.append(line)

    
    
    return (headerLines, lines)

@overload
def getSortedLineList(lineList: (list[str], [str])) -> list[str]: ...

@overload
def getSortedLineList(file: TextIOWrapper) -> list[str]: ...

def getSortedLineList(input, headerPrefix="! //", commentPrefix="!") -> list[str]:
    headerlines = []
    lines = []
    if type(input) is tuple:
        headerlines = input[0]
        lines = input[1]
    elif type(input) is TextIOWrapper:
        headerLines, lines = getLineList(file=input, headerPrefix=headerPrefix, commentPrefix=commentPrefix)

    decorated = [(line.removeprefix(commentPrefix).strip(" ./").lower(), i, line) for i, line in enumerate(lines)]
    decorated.sort()
    sortedLines = [line for lineS, i, line in decorated]

    return headerLines + sortedLines

