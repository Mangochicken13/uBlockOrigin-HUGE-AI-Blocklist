from io import TextIOWrapper
from typing import overload
from dataclasses import dataclass
import json

@dataclass
class LineConfig:
    header_prefix: str = "! //"
    comment_prefix: str = "!"
    url_prefix: str = "."
    apply_url_prefix: bool = False
    url_suffix: str = "/"
    apply_url_suffix: bool = False
    expand_domains: bool = False


def get_line_list(file: TextIOWrapper, config: LineConfig) -> (list[str], list[str]):
    header_lines = []
    lines: list[str] = []

    domains = []

    while True:
        position = file.tell()
        line = file.readline()

        # We hit a header
        if line.startswith(config.header_prefix):
            if len(lines) == 0: # keep appending header lines
                header_lines.append(line)
                continue
            file.seek(position) # reset to before the next header
            break

        # A non-header comment
        if line.startswith(config.comment_prefix):
            if len(lines) == 0:
                if config.expand_domains:
                    temp_line = line.strip(' !')
                    if temp_line.startswith('domains='):
                        domains.extend(json.loads(temp_line.removeprefix('domains=')))

                header_lines.append(line) # Assume that the comment is extra description
            else:
                # Add the comment into the normal lines
                # Will get sorted without the comment prefix in the sort function
                lines.append(line)
            continue

        if line == "\n":
            if len(lines) == 0:
                header_lines.append(line)
            # empty newlines aren't kept in the sorted lines under the header
            continue

        # We hit the end of the file
        if line == "":
            break

        if config.apply_url_prefix:
            if not line.startswith(config.url_prefix):
                line = config.url_prefix + line

        if config.apply_url_suffix:
            line = line.rstrip()
            if not line.endswith(config.url_suffix):
                line = line + config.url_suffix
            line = line + "\n"

        # Bandaid fix for a line that ends the file and is to be sorted
        line = line.rstrip() + "\n"

        # Expand the domains list for each real line
        # Don't use this when sorting, as that will put each domain after the entirety of that domain
        if config.expand_domains and len(domains) > 0:
            for d in domains:
                lines.append(d + line)

            continue

        lines.append(line)

    return (header_lines, lines)

@overload
def get_sorted_line_list(line_list: (list[str], list[str]), config: LineConfig) -> list[str]: ...
@overload
def get_sorted_line_list(file: TextIOWrapper, config: LineConfig) -> list[str]: ...

def get_sorted_line_list(file_input, config: LineConfig) -> list[str]:
    header_lines = []
    lines = []

    if isinstance(file_input, tuple):
        header_lines = file_input[0]
        lines = file_input[1]

    elif isinstance(file_input, TextIOWrapper):
        header_lines, lines = get_line_list(file=file_input, config=config)

    decorated = [
        (line.removeprefix(config.comment_prefix).strip(" ./").lower(), i, line)
        for i, line in enumerate(lines)
    ]
    decorated.sort()
    sorted_lines = [line for line_Sorted, i, line in decorated]

    return header_lines + sorted_lines

