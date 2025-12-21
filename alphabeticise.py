import argparse as arg
import io
import os

parser = arg.ArgumentParser(description="Organise domain names under each header alphabetically")

parser.add_argument("-f", "--file")

args = parser.parse_args()


def getLineList(_file: io.TextIOWrapper, headerPrefix="! //", commentPrefix="!") -> [str]:
    headerLines = []
    lines: [str] = []
    sortedLines = []

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

        lines.append(line.removesuffix("\n"))

    decorated = [(_line.removeprefix(commentPrefix).strip(" ."), i, _line) for i, _line in enumerate(lines)]
    #print(decorated)
    decorated.sort()
    sortedLines = [line+"\n" for _line, i, line in decorated]
    #print(sortedLines)
    
    return headerLines + sortedLines

def main():
    if (args.file):
        try:
            file = io.open(args.file, "r")
            print(f"File {args.file} opened successfully")
        except:
            print(f"Path {args.file} is not a valid file")
            return 1
        
        #print(args.file)

        targetFolder = os.path.dirname(args.file)
        targetName = os.path.basename(args.file)
        targetPath = os.path.join(targetFolder, "sorted_"+targetName)
        write_file = io.open(targetPath, "x")
        print(f"Writing to {targetPath}")

        while True:
            lines = getLineList(file)
            #print(lines)
            if (len(lines) == 0):
                break
            
            write_file.writelines(lines)
            write_file.write("\n")
        
        file.close()
        write_file.close()

        outputFile = io.open(targetPath, "r+")
        lastNewlineStartPosition = outputFile.tell()
        while True:
            line = outputFile.readline()
            if line == '': # end of file
                break

            if not (line == "\n"): # line is not a newline
                lastNewlineStartPosition = outputFile.tell()
        
        outputFile.seek(lastNewlineStartPosition)
        outputFile.truncate() # remove trailing newlines?
        outputFile.close()


main()