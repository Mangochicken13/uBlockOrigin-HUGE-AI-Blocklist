import optparse as opt
import warnings
from dataclasses import dataclass
from io import TextIOWrapper
from os import walk, makedirs, remove
from os.path import isfile, isdir, join, exists
from typing import overload
import get_line_list

opts = None
args = None

@dataclass
class FormatOptions:
    """
    :param str line_format: The format to place the line contents into. `"{url}"` in this string gets replaced with the line contents
    :param str engine: The engine that this line is being created for. Replaces `"{engine}"` in a string beginning with `header_prefix` or `comment_prefix`
    :param str header_prefix: The prefix expected for a commented header line
    :param str comment_prefix: The prefix expected for a commented line
    :param str comment_replacement: The string to replace the comment prefix with. Use when the engine doesn't use the default comment character (`!`)
    
    :param bool apply_prefix: Whether to check for and apply `line_prefix_to_apply`
    :param bool apply_suffix: Whether to check for and apply `line_suffix_to_apply`

    :param bool hosts_mode: Removes leading whitespace and periods, comments out lines that contain `/`
    """
    line_format: str
    engine: str
    header_prefix: str = "! //"
    comment_prefix: str = "!"
    comment_replacement: str = "!"
    apply_prefix: bool = False
    line_prefix_to_apply: str = ""
    apply_suffix: bool = False
    line_suffix_to_apply: str = ""

    # extra handling for the hosts.txt format
    hosts_mode: bool = False

def get_opts() -> opt.Values:
    parser = opt.OptionParser(
        description="Site blocklist generator script"
        )

    ## Formats
    formats = opt.OptionGroup(parser, "Formats")

    # Hosts
    formats.add_option(
        "--hosts",
        action='store_true', dest='create_hosts', default=True,
        help='Enable hosts.txt file creation (default)')
    formats.add_option(
        "--no-hosts",
        action='store_false', dest='create_hosts',
        help='Disable all hosts file creation. Includes --no-compile-hosts')
    formats.add_option(
        "--compile-hosts",
        action='store_true', dest='compile_hosts', default=True,
        help='Compile all hosts formats (default)')
    formats.add_option(
        "--no-compile-hosts",
        action='store_false', dest='compile_hosts',
        help="Don't compile the hosts.txt formats together")


    # uBlacklist
    formats.add_option(
        "--ublacklist",
        action='store_true', dest='create_ublacklist', default=True,
        help='Create uBlacklist file format (default)')
    formats.add_option(
        "--no-ublacklist", 
        action='store_false', dest='create_ublacklist',
        help="Don't create uBlacklist file format")


    # uBlockOrigin
    formats.add_option(
        "--ublockorigin", "--ubo", "--ublock",
        action='store_true', dest='create_ublockorigin', default=True,
        help='Create uBlockOrigin file (default)')
    formats.add_option(
        "--no-ublockorigin", "--no-ubo", "--no-ublock",
        action='store_false', dest='create_ublockorigin',
        help='Disable all uBlockOrigin file creation. Includes --no-compile-ublockorigin')
    formats.add_option(
        "--compile-ublockorigin", "--compile-ubo", "--compile-ublock",
        action='store_true', dest='compile_ublockorigin', default=True,
        help='Compile all uBlockOrigin formats (default)')
    formats.add_option(
        "--no-compile-ublockorigin", "--no-compile-ubo", "--no-compile-ublock",
        action='store_false', dest='compile_ublockorigin',
        help="Don't compile the uBlockOrigin formats together")

    parser.add_option_group(formats)


    ## Folders
    folders = opt.OptionGroup(parser, "Folders")
    folders.add_option(
        "--common-path",
        dest='common_path', default="Common",
        help='Path for the folder containing the common lists \nDefault = "Common"')
    folders.add_option(
        "--subpage-path",
        dest='subpage_path', default="SubPages",
        help='Path for the folder containing the subpage lists \nDefault = "SubPages"')
    folders.add_option(
        "--nuclear-path",
        dest='nuclear_path', default="Nuclear",
        help='Path for the folder containing the nuclear option lists \nDefault = "Nuclear"')
    folders.add_option(
        "--element-path",
        dest='element_path', default="Elements",
        help='Path for the folder containing additional elements added to the uBlockOrigin list \nDefault = "Elements"')

    parser.add_option_group(folders)

    # Nuclear
    parser.add_option(
        "-n", "--nuclear", 
        action='store_true', dest='create_nuclear_list', default=True)
    parser.add_option(
        "--no-nuclear",
        action='store_false', dest='create_nuclear_list',)

    # Export
    parser.add_option(
        "-o", "--output-folder",
        dest='output_path', default="Export",
        help='The folder to write the compiled and formatted files to')
    parser.add_option(
        "--overwrite",
        action='store_true', dest='overwrite', default=True,
        help='Overwrite existing exported files (default)')
    parser.add_option(
        "--no-overwrite",
        action='store_false', dest='overwrite',
        help="Don't allow ovewriting existing files in the export directory")

    loaded_opts, loaded_args = parser.parse_args()

    return loaded_opts, loaded_args

def format_line(line: str, format_options: FormatOptions) -> str:
    """
    Format a line appropriately for the target engine & format

    :param str line: The contents of the line to be formatted
    :return: The formatted line according to `format_options`. Returns `format_options.format` if `{url}` is not present and `line` is not a comment
    """

    if line.startswith(format_options.header_prefix) or line.startswith(format_options.comment_prefix):
        line = line.replace("{engine}", format_options.engine)
        # replace the comment character for other file types
        line = line.replace(format_options.comment_prefix, format_options.comment_replacement, 1)
        return line

    if line.rstrip() == "":
        return line

    if format_options.hosts_mode:
        # remove leading periods
        # still continue to allow the www. prefix to be applied?
        line = line.strip(" .")

        if "/" in line:
            # afaik the hosts format doesn't allow individual pages? still return the line commented though
            return "#       " + line

    if format_options.apply_prefix:
        if not line.startswith(format_options.line_prefix_to_apply):
            line = format_options.line_prefix_to_apply + line

    if format_options.apply_suffix:
        line = line.rstrip()
        if not line.endswith(format_options.line_suffix_to_apply):
            line = line + format_options.line_suffix_to_apply
        line = line + "\n"

    line_format = format_options.format.rstrip() + "\n" # Normalise the format line ending, add if not present
    return line_format.replace("{url}", line.rstrip())

def get_files(folder: str) -> list[str]:
    files = []
    if isdir(folder):
        files.extend([join(dirpath, f) for (dirpath, dirnames, filenames) in walk(folder) for f in filenames])
    else:
        if isfile(folder):
            warnings.warn(f"path '{folder}' is a file, proceeding with only {folder} in the file list")
            files.append(folder)
        else:
            warnings.warn(f"path '{folder}' is not a file or dir, proceeding with no files")

    return files

@overload
def get_files_sorted(folder: str) -> list[str]: ...
@overload
def get_files_sorted(files: list[str]) -> list[str]: ...

def get_files_sorted(file_input) -> list[str]:
    if isinstance(file_input, str):
        files = get_files(file_input)
        return sorted(files, key=str.lower)

    if isinstance(file_input, list[str]):
        return sorted(file_input, key=str.lower)

def write_formatted_lines_to_file(input_file_paths: list[str], output_file: TextIOWrapper, format_options: FormatOptions):

    line_config = get_line_list.LineConfig(expand_domains=True)

    # write all the formatted lines from the appropriate files
    for input_file in input_file_paths:
        if isfile(input_file):
            with open(input_file, "r", encoding="utf-8") as f:
                while True:
                    header_lines, lines = get_line_list.get_line_list(f, line_config)
                    if (len(header_lines) == 0 and len(lines) == 0):
                        output_file.write('\n')
                        break
                    
                    output_file.writelines([
                        format_line(line, format_options)
                        for line in header_lines + lines
                    ])

                    output_file.write("\n")

def try_write_to_path(path: str, input_file_paths: list[str], format_options: FormatOptions) -> bool:

    if exists(path) and isfile(path):
        if opts.overwrite:
            remove(path)
        else:
            warnings.warn(f"Target file {path} exists and overwriting is disabled, skipping")
            return False

    elif isdir(path):
        warnings.warn(f"Target file {path} is a directory, skipping")
        return False

    with open(path, "x", encoding="utf-8") as f:
        write_formatted_lines_to_file(input_file_paths, f, format_options)
        print(f"Successfully wrote {path}")
        return True

def compile_files(input_file_paths: list[str], output_file: str, output_header: str) -> bool:
    if exists(output_file):
        if isdir(output_file):
            warnings.warn(f"Targeted path {output_file} is a directory, cancelling writing from {input_file_paths}")
            return False

        if opts.overwrite:
            remove(output_file)
        else:
            warnings.warn(f"Target file {output_file} exists and overwriting is disabled, skipping")
            return False

    with open(output_file, "x", encoding="utf-8") as f:
        f.write(output_header+'\n')
        for path in input_file_paths:
            if isfile(path):
                with open(path, "rt", encoding="utf-8") as input_file:
                    for line in input_file:
                        f.write(line)

                    f.write('\n')

    print(f"Successfully compiled {output_file}")
    return True

def main():
    global opts, args
    opts, args = get_opts()

    common_files = get_files_sorted(opts.common_path)
    subpage_files = get_files_sorted(opts.subpage_path)
    nuclear_files = get_files_sorted(opts.nuclear_path)
    element_files = get_files_sorted(opts.element_path)

    if isfile(opts.output_path):
        warnings.warn(f"Output path {opts.output_path} is a file, not a directiory. Cancelling operations")
        return

    if not exists(opts.output_path):
        makedirs(opts.output_path)

    if opts.create_ublockorigin:
        # TODO: move this into the arguments
        ublock_formats = {
            "google": 'google.com##a[href*="{url}"]:upward(2):remove()',
            "duckduckgo": 'duckduckgo.com##a[href*="{url}"]:upward(figure):upward(1):remove()',
            "bing": 'bing.com##a[href*="{url}"]:upward(li):remove()',
        }

        format_options = FormatOptions("", "")
        element_format = FormatOptions("{url}", "")

        written_files = []
        written_files_nuclear = []

        for engine, line_format in ublock_formats.items():
            format_options.line_format = line_format
            format_options.engine = engine

            target_path = join(opts.output_path, format_options.engine + "-list_uBlockOrigin.txt")

            was_file_written = try_write_to_path(
                target_path,
                common_files + subpage_files,
                format_options
            )

            if was_file_written:
                # Append extra elements to ublock format
                with open(target_path, "a", encoding="utf-8") as f:
                    for file in element_files:
                        with open(file, "rt", encoding="utf-8") as r:
                            for line in r:
                                f.write(format_line(line, element_format))

                written_files.append(target_path)

        if opts.create_nuclear_list:
            for engine, line_format in ublock_formats.items():
                format_options.line_format = line_format
                format_options.engine = engine + " (Nuclear)"

                target_path = join(opts.output_path, "Nuclear_" + engine + "-list_uBlockOrigin.txt")

                was_file_written = try_write_to_path(target_path, nuclear_files, format_options)

                if was_file_written:
                    written_files_nuclear.append(target_path)

        # grab all the written files and add them together
        if opts.compile_ublockorigin:
            target_path = join(opts.output_path, "list_uBlockOrigin.txt")
            compile_files(written_files, target_path, "! Title: Huge AI Blocklist (Compiled)\n")

            if opts.create_nuclear_list:
                target_path = join(opts.output_path, "Nuclear_list_uBlockOrigin.txt")
                compile_files(written_files, target_path, "! Title: Huge AI Blocklist (Nuclear) (Compiled)\n")

    if opts.create_ublacklist:
        # TODO: move this into the arguments
        ublacklist_format = FormatOptions(
            line_format='*://*{url}*',
            engine="uBlacklist",
            comment_replacement="#",
            apply_prefix=True,
            line_prefix_to_apply=".",
            apply_suffix=True,
            line_suffix_to_apply="/"
        )

        target_path = join(opts.output_path, "list_uBlacklist.txt")

        was_file_written = try_write_to_path(
            target_path,
            common_files + subpage_files,
            ublacklist_format
        )

        if opts.create_nuclear_list:
            target_path = join(opts.output_path, "Nuclear_list_uBlacklist.txt")

            was_file_written = try_write_to_path(target_path, nuclear_files, ublacklist_format)

    if opts.create_hosts:
        hosts_formats = [
            FormatOptions(
                line_format='0.0.0.0 {url}',
                engine='hosts',
                comment_replacement="#",
                hosts_mode=True
            ),
            FormatOptions(
                line_format='0.0.0.0 www{url}',
                engine='hosts-www',
                comment_replacement="#",
                apply_prefix=True,
                line_prefix_to_apply='.',
                hosts_mode=True
            )
        ]

        written_files = []

        for format_option in hosts_formats:
            target_path = join(opts.output_path, format_option.engine + ".txt")

            was_file_written = try_write_to_path(target_path, common_files, format_option)
            if was_file_written:
                written_files.append(target_path)

        if opts.compile_hosts:
            target_path = join(opts.output_path, "list_hosts.txt")
            compile_files(written_files, target_path, "# Title: Huge AI Blocklist (Compiled)\n")


if __name__ == '__main__':
    main()
