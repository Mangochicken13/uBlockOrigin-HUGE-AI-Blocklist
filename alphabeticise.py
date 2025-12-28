import argparse as arg
import getLineList
import os

parser = arg.ArgumentParser(description="Organise domain names under each header alphabetically")

parser.add_argument("file")

args = parser.parse_args()

def main():
    if (args.file):
        try:
            file = open(args.file, "r")
            print(f"File {args.file} opened successfully")
        except:
            print(f"Path {args.file} is not a valid file")
            return 1
        
        #print(args.file)

        targetFolder = os.path.dirname(args.file)
        targetName = os.path.basename(args.file)
        targetPath = os.path.join(targetFolder, "sorted_" + targetName)
        write_file = open(targetPath, "x")
        print(f"Writing to {targetPath}")

        config = getLineList.LineConfig()

        while True:
            lines = getLineList.getSortedLineList(file, config)
            #print(lines)
            if (len(lines) == 0):
                break
            
            write_file.writelines(lines)
            write_file.write("\n")
        
        file.close()
        write_file.close()

        outputFile = open(targetPath, "r+")
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

if __name__ == "__main__":
    main()