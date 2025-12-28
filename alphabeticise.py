import argparse as arg
import os
import get_line_list

parser = arg.ArgumentParser(description="Organise domain names under each header alphabetically")

parser.add_argument("file")

args = parser.parse_args()

def main():
    if args.file:
        try:
            file = open(args.file, "r", encoding="utf-8")
            print(f"File {args.file} opened successfully")
        except OSError:
            print(f"Path {args.file} is not a valid file")
            return 1

        target_folder = os.path.dirname(args.file)
        target_name = os.path.basename(args.file)
        target_path = os.path.join(target_folder, "sorted_" + target_name)
        with open(target_path, "x", encoding="utf-8") as write_file:
            print(f"Writing to {target_path}")

            config = get_line_list.LineConfig()

            while True:
                lines = get_line_list.get_sorted_line_list(write_file, config)
                #print(lines)
                if len(lines) == 0:
                    break

                write_file.writelines(lines)
                write_file.write("\n")

            file.close()
            write_file.close()

        with open(target_path, "r+", encoding="utf-8") as output_file:
            last_newline_start_position = output_file.tell()
            while True:
                line = output_file.readline()
                if line == '': # end of file
                    break

                if not line == "\n": # line is not a newline
                    last_newline_start_position = output_file.tell()

            output_file.seek(last_newline_start_position)
            output_file.truncate() # remove trailing newlines?

if __name__ == "__main__":
    main()
