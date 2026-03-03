import argparse as arg
import warnings
from dataclasses import dataclass
from io import TextIOWrapper
from os import walk, makedirs, remove
from os.path import isfile, isdir, join, exists
from typing import overload
import get_line_list

@dataclass
class Options:
    """
    """

    create_hosts: bool = True
    compile_hosts: bool = False
    create_ublacklist: bool = True
    create_ublockorigin: bool = True
    compile_ublockorigin: bool = True
    create_nuclear_lists: bool = True
    
    # Folders
    list_folder: str = "Lists"
    common_list_path: str = "Common"
    subpage_list_path: str = "SubPages"
    nuclear_list_path: str = "Nuclear"
    element_list_path: str = "Elements"

    output_path: str = "Export"
    overwrite_files: bool = True
    clean_output_folder: bool = False



# TODO: go check alyce discord for get opts() refactor tips


@dataclass
class FormatOptions:
    """
    :param list[str] line_formats: The formats to place the line contents into. `"{url}"` in this string gets replaced with the line contents
    :param str engine: The engine that this line is being created for. Replaces `"{engine}"` in a string beginning with `header_prefix` or `comment_prefix`
    :param str header_prefix: The prefix expected for a commented header line
    :param str comment_prefix: The prefix expected for a commented line
    :param str comment_replacement: The string to replace the comment prefix with. Use when the engine doesn't use the default comment character (`!`)
    
    :param bool apply_prefix: Whether to check for and apply `line_prefix_to_apply`
    :param bool apply_suffix: Whether to check for and apply `line_suffix_to_apply`

    :param bool hosts_mode: Removes leading whitespace and periods, comments out lines that contain `/`
    """
    def __init__(self) -> None:
        self._line_formats: list[str] = ["{url}"]
        self.engine = ""
        self.header_prefix = "! //"
        self.comment_prefix = "!"
        self.comment_prefix_replacement = "!"
        self.apply_prefix = False
        self.line_prefix_to_apply = ""
        self.apply_suffix = False
        self.line_suffix_to_apply = ""
        self.hosts_mode = False

    # Guarding against formats being assigned without a newline character included
    @property
    def line_formats(self) -> list[str]:
        return self._line_formats

    @line_formats.setter
    def line_formats(self, value: list[str]):
        input_formats = value
        output_formats: list[str] = []
        for format in input_formats:
            format = format.rstrip() + "\n"
            output_formats.append(format)
        self._line_formats = output_formats.copy()

    @line_formats.deleter
    def line_formats(self):
        del self._line_formats

    engine: str = ""
    header_prefix: str = "! //"
    comment_prefix: str = "!"
    comment_prefix_replacement: str = "!"
    apply_prefix: bool = False
    line_prefix_to_apply: str = ""
    apply_suffix: bool = False
    line_suffix_to_apply: str = ""

    # extra handling for the hosts.txt format
    hosts_mode: bool = False

def build_parser() -> arg.ArgumentParser:
    parser = arg.ArgumentParser(
            description="Site blocklist generator and formatter script"
    )

    formats = parser.add_argument_group(title="Formats")
    _ = formats.add_argument(
        "--hosts",
        action=arg.BooleanOptionalAction, dest='create_hosts', default=True,
        help='Enable hosts.txt file creation (default)')
    # _ = formats.add_argument(
    #     "--no-hosts",
    #     action='store_false', dest='create_hosts',
    #     help='Disable all hosts file creation. Includes --no-compile-hosts')
    # _ = formats.add_option(
    #     "--compile-hosts",
    #     action='store_true', dest='compile_hosts', default=True,
    #     help='Compile all hosts formats (default)')
    # _ = formats.add_option(
    #     "--no-compile-hosts",
    #     action='store_false', dest='compile_hosts',
    #     help="Don't compile the hosts.txt formats together")

    # uBlacklist
    _ = formats.add_argument(
        "--ublacklist",
        action=arg.BooleanOptionalAction, dest='create_ublacklist', default=True,
        help='Create uBlacklist file format (default)')
    # _ = formats.add_argument(
    #     "--no-ublacklist", 
    #     action='store_false', dest='create_ublacklist',
    #     help="Don't create uBlacklist file format")

    # uBlockOrigin
    _ = formats.add_argument(
        "--ublockorigin", "--ubo", "--ublock",
        action=arg.BooleanOptionalAction, dest='create_ublockorigin', default=True,
        help='Create uBlockOrigin file (default)')
    # _ = formats.add_argument(
    #     "--no-ublockorigin", "--no-ubo", "--no-ublock",
    #     action='store_false', dest='create_ublockorigin',
    #     help='Disable all uBlockOrigin file creation. Includes --no-compile-ublockorigin')
    _ = formats.add_argument(
        "--compile-ublockorigin", "--compile-ubo", "--compile-ublock",
        action=arg.BooleanOptionalAction, dest='compile_ublockorigin', default=True,
        help='Compile all uBlockOrigin formats (default)')
    # _ = formats.add_argument(
    #     "--no-compile-ublockorigin", "--no-compile-ubo", "--no-compile-ublock",
    #     action='store_false', dest='compile_ublockorigin',
    #     help="Don't compile the uBlockOrigin formats together")

    ## Folders
    folders = parser.add_argument_group("Folders")
    _ = folders.add_argument(
        "--list-path",
        dest='list_path', default="Lists",
        help='Parent folder where all list subfolders are located \nDefault = "Lists"')
    _ = folders.add_argument(
        "--common-path",
        dest='common_path', default="Common",
        help='Path for the folder containing the common lists \nDefault = "Common"')
    _ = folders.add_argument(
        "--subpage-path",
        dest='subpage_path', default="SubPages",
        help='Path for the folder containing the subpage lists \nDefault = "SubPages"')
    _ = folders.add_argument(
        "--nuclear-path",
        dest='nuclear_path', default="Nuclear",
        help='Path for the folder containing the nuclear option lists \nDefault = "Nuclear"')
    _ = folders.add_argument(
        "--element-path",
        dest='element_path', default="Elements",
        help='Path for the folder containing additional elements added to the uBlockOrigin list \nDefault = "Elements"')

    # Nuclear
    _ = parser.add_argument(
        "-n", "--nuclear", 
        action=arg.BooleanOptionalAction, dest='create_nuclear_list', default=True)
    # _ = parser.add_argument(
    #     "--no-nuclear",
    #     action='store_false', dest='create_nuclear_list',)

    # Export
    _ = parser.add_argument(
        "-o", "--output-folder",
        dest='output_path', default="Export",
        help='The folder to write the compiled and formatted files to')
    _ = parser.add_argument(
        "--overwrite",
        action=arg.BooleanOptionalAction, dest='overwrite', default=True,
        help='Overwrite existing exported files (default)')
    # _ = parser.add_argument(
    #     "--no-overwrite",
    #     action='store_false', dest='overwrite',
    #     help="Don't allow ovewriting existing files in the export directory")

    return parser

# def get_opts() -> tuple[opt.Values, list[str]]:
#     parser = opt.OptionParser(
#         description="Site blocklist generator script"
#     )
#
#     ## Formats
#     formats = opt.OptionGroup(parser, "Formats")
#
#     # Hosts
#     _ = formats.add_option(
#         "--hosts",
#         action='store_true', dest='create_hosts', default=True,
#         help='Enable hosts.txt file creation (default)')
#     _ = formats.add_option(
#         "--no-hosts",
#         action='store_false', dest='create_hosts',
#         help='Disable all hosts file creation. Includes --no-compile-hosts')
#     # _ = formats.add_option(
#     #     "--compile-hosts",
#     #     action='store_true', dest='compile_hosts', default=True,
#     #     help='Compile all hosts formats (default)')
#     # _ = formats.add_option(
#     #     "--no-compile-hosts",
#     #     action='store_false', dest='compile_hosts',
#     #     help="Don't compile the hosts.txt formats together")
#
#
#     # uBlacklist
#     _ = formats.add_option(
#         "--ublacklist",
#         action='store_true', dest='create_ublacklist', default=True,
#         help='Create uBlacklist file format (default)')
#     _ = formats.add_option(
#         "--no-ublacklist", 
#         action='store_false', dest='create_ublacklist',
#         help="Don't create uBlacklist file format")
#
#
#     # uBlockOrigin
#     _ = formats.add_option(
#         "--ublockorigin", "--ubo", "--ublock",
#         action='store_true', dest='create_ublockorigin', default=True,
#         help='Create uBlockOrigin file (default)')
#     _ = formats.add_option(
#         "--no-ublockorigin", "--no-ubo", "--no-ublock",
#         action='store_false', dest='create_ublockorigin',
#         help='Disable all uBlockOrigin file creation. Includes --no-compile-ublockorigin')
#     _ = formats.add_option(
#         "--compile-ublockorigin", "--compile-ubo", "--compile-ublock",
#         action='store_true', dest='compile_ublockorigin', default=True,
#         help='Compile all uBlockOrigin formats (default)')
#     _ = formats.add_option(
#         "--no-compile-ublockorigin", "--no-compile-ubo", "--no-compile-ublock",
#         action='store_false', dest='compile_ublockorigin',
#         help="Don't compile the uBlockOrigin formats together")
#
#     _ = parser.add_option_group(formats)
#
#
#     ## Folders
#     folders = opt.OptionGroup(parser, "Folders")
#     _ = folders.add_option(
#         "--list-path",
#         dest='list_path', default="Lists",
#         help='Parent folder where all list subfolders are located \nDefault = "Lists"')
#     _ = folders.add_option(
#         "--common-path",
#         dest='common_path', default="Common",
#         help='Path for the folder containing the common lists \nDefault = "Common"')
#     _ = folders.add_option(
#         "--subpage-path",
#         dest='subpage_path', default="SubPages",
#         help='Path for the folder containing the subpage lists \nDefault = "SubPages"')
#     _ = folders.add_option(
#         "--nuclear-path",
#         dest='nuclear_path', default="Nuclear",
#         help='Path for the folder containing the nuclear option lists \nDefault = "Nuclear"')
#     _ = folders.add_option(
#         "--element-path",
#         dest='element_path', default="Elements",
#         help='Path for the folder containing additional elements added to the uBlockOrigin list \nDefault = "Elements"')
#
#     _ = parser.add_option_group(folders)
#
#     # Nuclear
#     _ = parser.add_option(
#         "-n", "--nuclear", 
#         action='store_true', dest='create_nuclear_list', default=True)
#     _ = parser.add_option(
#         "--no-nuclear",
#         action='store_false', dest='create_nuclear_list',)
#
#     # Export
#     _ = parser.add_option(
#         "-o", "--output-folder",
#         dest='output_path', default="Export",
#         help='The folder to write the compiled and formatted files to')
#     _ = parser.add_option(
#         "--overwrite",
#         action='store_true', dest='overwrite', default=True,
#         help='Overwrite existing exported files (default)')
#     _ = parser.add_option(
#         "--no-overwrite",
#         action='store_false', dest='overwrite',
#         help="Don't allow ovewriting existing files in the export directory")
#
#     loaded_opts, loaded_args = parser.parse_args()
#
#     return loaded_opts, loaded_args

def format_line(line: str, format_options: FormatOptions) -> list[str]:
    """
    Format a line appropriately for the target engine & format

    :param str line: The contents of the line to be formatted
    :return: The formatted line according to `format_options`. Returns `format_options.line_format` if `{url}` is not present and `line` is not a comment
    """

    if line.startswith(format_options.header_prefix) or line.startswith(format_options.comment_prefix):
        line = line.replace("{engine}", format_options.engine)
        # replace the comment character for other file types
        line = line.replace(format_options.comment_prefix, format_options.comment_prefix_replacement, 1)
        return [line]

    if line.rstrip() == "":
        return [line]

    if format_options.hosts_mode:
        # remove leading periods
        # still continue to allow the www. prefix to be applied?
        line = line.strip(" .")

        if "/" in line:
            # afaik the hosts format doesn't allow individual pages? still return the line commented though
            return ["#       " + line]

    if format_options.apply_prefix:
        if not line.startswith(format_options.line_prefix_to_apply):
            line = format_options.line_prefix_to_apply + line

    if format_options.apply_suffix:
        line = line.rstrip()
        if not line.endswith(format_options.line_suffix_to_apply):
            line = line + format_options.line_suffix_to_apply
        line = line + "\n"

    lines: list[str] = []
    for format in format_options.line_formats: 
        lines.append(format.replace("{url}", line.rstrip()))

    return lines

def get_files(folder: str) -> list[str]:
    files: list[str] = []
    if isdir(folder):
        files.extend([
            join(dirpath, f)
            for (dirpath, _dirnames, filenames) in walk(folder)
            for f in filenames
        ])
    else:
        if isfile(folder):
            warnings.warn(f"path '{folder}' is a file, proceeding with only {folder} in the file list")
            files.append(folder)
        else:
            warnings.warn(f"path '{folder}' is not a file or dir, proceeding with no files")

    return files

@overload
def get_files_sorted(folder: str, /) -> list[str]: ...
@overload
def get_files_sorted(files: list[str], /) -> list[str]: ...

def get_files_sorted(input: str | list[str]) -> list[str]:
    if isinstance(input, str):
        files = get_files(input)
        return sorted(files, key=str.lower)

    if isinstance(input, list):
        return sorted(input, key=str.lower)

def write_formatted_lines_to_file(input_file_paths: list[str], output_file: TextIOWrapper, format_options: FormatOptions):

    line_config = get_line_list.LineConfig(expand_domains=True)

    # write all the formatted lines from the appropriate files
    for input_file in input_file_paths:
        if isfile(input_file):
            with open(input_file, "r", encoding="utf-8") as f:
                while True:
                    header_lines, lines = get_line_list.get_line_list(f, line_config)
                    if (len(header_lines) == 0 and len(lines) == 0):
                        _ = output_file.write('\n')
                        break
                    
                    lines_to_write: list[str] = []
                    for line in (header_lines + lines):
                        lines_to_write.extend(format_line(line, format_options))
                    output_file.writelines(lines_to_write)

                    _ = output_file.write("\n")

def try_write_to_path(path: str, input_file_paths: list[str], format_options: FormatOptions, overwrite: bool) -> bool:

    if exists(path) and isfile(path):
        if overwrite:
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

def compile_files(input_file_paths: list[str], output_file: str, output_header: str, overwrite: bool, remove_sources: bool = False) -> bool:
    if exists(output_file):
        if isdir(output_file):
            warnings.warn(f"Targeted path {output_file} is a directory, cancelling writing from {input_file_paths}")
            return False

        if overwrite:
            remove(output_file)
        else:
            warnings.warn(f"Target file {output_file} exists and overwriting is disabled, skipping")
            return False

    with open(output_file, "x", encoding="utf-8") as f:
        _ = f.write(output_header+'\n')
        for path in input_file_paths:
            if isfile(path):
                with open(path, "rt", encoding="utf-8") as input_file:
                    for line in input_file:
                        _ = f.write(line)

                    _ = f.write('\n')
                if remove_sources:
                    remove(path)

    print(f"Successfully compiled {output_file}")
    return True

def main(config: Options):
    common_files = get_files_sorted(join(config.list_folder, config.common_list_path))
    subpage_files = get_files_sorted(join(config.list_folder, config.subpage_list_path))
    nuclear_files = get_files_sorted(join(config.list_folder, config.nuclear_list_path))
    element_files = get_files_sorted(join(config.list_folder, config.element_list_path))

    if isfile(config.output_path):
        warnings.warn(f"Output path {config.output_path} is a file, not a directiory. Cancelling operations")
        return

    if not exists(config.output_path):
        makedirs(config.output_path)

    if config.create_ublockorigin:
        # TODO: move this into the arguments
        ublock_formats = {
            "google": ['google.com##a[href*="{url}"]:upward(2):remove()'],
            "duckduckgo": ['duckduckgo.com##a[href*="{url}"]:upward(figure):upward(1):remove()'],
            "bing": ['bing.com##a[href*="{url}"]:upward(li):remove()'],
        }

        format_options = FormatOptions()
        element_format = FormatOptions()
        element_format.line_formats = ["{url}"]

        written_files = []
        written_files_nuclear = []

        for engine, line_format in ublock_formats.items():
            format_options.line_formats = line_format
            format_options.engine = engine

            target_path = join(config.output_path, format_options.engine + "-list_uBlockOrigin.txt")

            was_file_written = try_write_to_path(
                target_path,
                common_files + subpage_files,
                format_options,
                config.overwrite_files
            )

            if was_file_written:
                # Append extra elements to ublock format
                with open(target_path, "a", encoding="utf-8") as f:
                    for file in element_files:
                        with open(file, "rt", encoding="utf-8") as r:
                            for line in r:
                                _ = f.writelines(format_line(line, element_format))

                written_files.append(target_path)

        if config.create_nuclear_lists:
            for engine, line_format in ublock_formats.items():
                format_options.line_formats = line_format
                format_options.engine = engine + " (Nuclear)"

                target_path = join(config.output_path, "Nuclear_" + engine + "-list_uBlockOrigin.txt")

                was_file_written = try_write_to_path(target_path, nuclear_files, format_options, config.overwrite_files)

                if was_file_written:
                    written_files_nuclear.append(target_path)

        # grab all the written files and add them together
        if config.compile_ublockorigin:
            target_path = join(config.output_path, "list_uBlockOrigin.txt")
            _ = compile_files(written_files, target_path, "! Title: Huge AI Blocklist (Compiled)\n", config.overwrite_files)

            if config.create_nuclear_lists:
                target_path = join(config.output_path, "Nuclear_list_uBlockOrigin.txt")
                _ = compile_files(written_files, target_path, "! Title: Huge AI Blocklist (Nuclear) (Compiled)\n", config.overwrite_files)

    if config.create_ublacklist:
        # TODO: move this into the arguments
        ublacklist_format = FormatOptions()
        ublacklist_format.line_formats = ['*://*{url}*']
        ublacklist_format.engine = "uBlacklist"
        ublacklist_format.comment_prefix_replacement = "#"
        ublacklist_format.apply_prefix = True
        ublacklist_format.line_prefix_to_apply = "."
        ublacklist_format.apply_suffix = True
        ublacklist_format.line_suffix_to_apply = "/"

        target_path = join(config.output_path, "list_uBlacklist.txt")

        was_file_written = try_write_to_path(
            target_path,
            common_files + subpage_files,
            ublacklist_format,
            config.overwrite_files
        )

        if config.create_nuclear_lists:
            target_path = join(config.output_path, "Nuclear_list_uBlacklist.txt")

            was_file_written = try_write_to_path(target_path, nuclear_files, ublacklist_format, config.overwrite_files)

    if config.create_hosts:
        hosts_format = FormatOptions()
        hosts_format.line_formats = ['0.0.0.0 {url}', '0.0.0.0 www.{url}']
        hosts_format.engine='hosts'
        hosts_format.comment_prefix_replacement="#"
        hosts_format.hosts_mode=True

        written_files = []

        target_path = join(config.output_path, hosts_format.engine + ".txt")

        _ = try_write_to_path(target_path, common_files, hosts_format, config.overwrite_files)


def get_opts() -> Options:
    parser = build_parser()
    args = parser.parse_args()
    options = Options(**vars(args))  # pyright: ignore[reportAny]

    return options


if __name__ == '__main__':
    config = get_opts()
    main(config)
