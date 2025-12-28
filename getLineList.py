from io import TextIOWrapper
from typing import overload
from dataclasses import dataclass
import json

@dataclass
class LineConfig:
    headerPrefix: str = "! //"
    commentPrefix: str = "!"
    urlPrefix: str = "."
    applyUrlPrefix: bool = False
    urlSuffix: str = "/"
    applyUrlSuffix: bool = False
    expandDomains: bool = False


def getLineList(file: TextIOWrapper, config: LineConfig) -> (list[str], list[str]):
    headerLines = []
    lines: list[str] = []

    domains = []

    while True:
        position = file.tell()
        line = file.readline()

        # We hit a header
        if (line.startswith(config.headerPrefix)):
            if len(lines) == 0: # keep appending header lines
                headerLines.append(line)
                continue
            file.seek(position) # reset to before the next header
            break

        # A non-header comment
        elif (line.startswith(config.commentPrefix)):
            if len(lines) == 0:
                if config.expandDomains:
                    tempLine = line.strip(' !')
                    if tempLine.startswith('domains='):
                        domains.extend(json.loads(tempLine.removeprefix('domains=')))
                    
                headerLines.append(line) # Assume that the comment is extra description
            else:
                lines.append(line) # Add the comment into the normal lines, sorted without the comment prefix in the sort function
            continue

        if (line == "\n"):
            if len(lines) == 0:
                headerLines.append(line)
            # empty newlines aren't kept in the sorted lines under the header
            continue 

        # We hit the end of the file
        if (line == ""):
            break
        
        if config.applyUrlPrefix:
            if not line.startswith(config.urlPrefix):
                line = config.urlPrefix + line
        
        if config.applyUrlSuffix:
            line = line.rstrip()
            if not line.endswith(config.urlSuffix):
                line = line + config.urlSuffix
            line = line + "\n"

        # Bandaid fix for a line that ends the file and is to be sorted
        line = line.rstrip() + "\n" 
        
        # Expand the domains list for each real line
        # Don't use this when sorting, as that will put each domain after the entirety of that domain
        if config.expandDomains and len(domains) > 0:
            for d in domains:
                lines.append(d + line)
            
            continue

        lines.append(line)

    return (headerLines, lines)

@overload
def getSortedLineList(lineList: (list[str], list[str]), config: LineConfig) -> list[str]: ...

@overload
def getSortedLineList(file: TextIOWrapper, config: LineConfig) -> list[str]: ...

def getSortedLineList(input, config: LineConfig) -> list[str]:
    headerlines = []
    lines = []

    if type(input) is tuple:
        headerlines = input[0]
        lines = input[1]

    elif type(input) is TextIOWrapper:
        headerLines, lines = getLineList(file=input, config=config)

    decorated = [
        (line.removeprefix(config.commentPrefix).strip(" ./").lower(), i, line)
        for i, line in enumerate(lines)
    ]
    decorated.sort()
    sortedLines = [line for line_Sorted, i, line in decorated]

    return headerLines + sortedLines

