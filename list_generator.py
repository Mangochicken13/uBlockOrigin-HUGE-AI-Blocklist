import optparse as opt
import warnings
import logging
import __getLineList__
from os import walk, path, makedirs, remove
from os.path import isfile, isdir, join, exists
from typing import overload


def getOpts() -> opt.Values:
    parser = opt.OptionParser(
        description="Site blocklist generator script"
        )
    
    formats = opt.OptionGroup(parser, "Formats")

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

    formats.add_option(
        "--ublacklist",
        action='store_true', dest='create_ublacklist', default=True,
        help='Create uBlacklist file format (default)')
    formats.add_option(
        "--no-ublacklist", 
        action='store_false', dest='create_ublacklist',
        help="Don't create uBlacklist file format")

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

    parser.add_option(
        "-n", "--nuclear", 
        action='store_true', dest='create_nuclear_list', default=True)
    




    parser.add_option(
        "--common-path",
        dest='commonPath', default="Collections",)
    parser.add_option(
        "--nuclear-path",
        dest='nuclearPath', default="Nuclear",
        help='Path for the folder containing the nuclear option lists')
    parser.add_option(
        "--element-path",
        dest='elementPath', default="Elements",
        help='Path for the folder containing additional elements added to the uBlockOrigin list')

    parser.add_option(
        "-o", "--output-folder",
        dest='outputPath', default="Export",
        help='')

    opts, args = parser.parse_args()

    return opts

def formatLine(_line: str, _format: str, _engine: str, _headerPrefix: str = "! //", _commentPrefix = "!", _commentReplacement = '!') -> str:
    """
    Format a line appropriately for the target engine & format

    :param str _line: The contents of the line to be formatted
    :param str _format: The format to place the line contents into. `{url}` in this string is to be replaced with :param str line:
    :param str _engine: The engine that this line is being created for. Replaces `{engine}` in a string beginning with :param str headerPrefix: or :param str commentPrefix:
    :param str headerPrefix: The prefix expected for a commented header line
    :param str commentPrefix: The prefix expected for a commented line
    :param str commentReplacement: The string to replace the comment prefix with. Use when the engine doesn't use the default comment character `!`
    
    :return: The formatted line. Returns :param str _format
    """
    _format = _format.rstrip() + "\n" # Normalise the format line ending, add if not present
    if _line.startswith(_headerPrefix) or _line.startswith(_commentPrefix):
        return _line.replace("{engine}", _engine).replace(_commentPrefix, _commentReplacement, 1) # replace the comment character for other file types
    
    return _format.replace("{url}", _line.rstrip())

def getFiles(_folder: str) -> [str]:
    files = []
    if isdir(_folder):
        files.extend([join(dirpath, f) for (dirpath, dirnames, filenames) in walk(_folder) for f in filenames])
    else:
        if isfile(_folder):
            warnings.warn(f"path '{_folder}' is a file, proceeding with only {_folder} in the common file list")
            files.append(_folder)
        else:
            warnings.warn(f"path '{_folder}' is not a file or dir, proceeding with no common files")
    
    return files

@overload
def getFiles_Sorted(_folder: str) -> [str]: ...
@overload
def getFiles_Sorted(_files: [str]) -> [str]: ...

def getFiles_Sorted(_input) -> [str]:
    print(type(_input), _input)
    if type(_input) == str:
        files = getFiles(_input)
        return sorted(files, key=str.lower)
    if type(_input) == [str]:
        return sorted(_input, key=str.lower)


def compileFiles(_filePaths: [str], _outputFile: str, outputHeader: str, _overwrite: bool = True) -> bool:
    if exists(_outputFile):
        if isdir(_outputFile):
            warnings.warn(f"Targeted path {_outputFile} is a directory, cancelling writing from {_filePaths}")
            return False
        if isfile(_outputFile):
            remove(_outputFile)
    
    with open(_outputFile, "x") as outputFile:
        outputFile.write(outputHeader+'\n')
        for path in _filePaths:
            if isfile(path):
                with open(path, "r") as inputFile:
                    for line in inputFile:
                        outputFile.write(line)
                    
                    outputFile.write('\n')
    
    return True
    

def main():
    opts = getOpts()
    #print(opts)
    
    commonFiles = getFiles_Sorted(opts.commonPath)
    print(commonFiles, "\n")
    
    nuclearFiles = getFiles_Sorted(opts.nuclearPath)
    print(nuclearFiles, "\n")

    elementFiles = getFiles_Sorted(opts.elementPath)
    print(elementFiles, "\n")

    if isfile(opts.outputPath):
        warnings.warn(f"Output path {opts.outputPath} is a file, not a directiory. Cancelling compilation")
        return
    elif not exists(opts.outputPath):
        makedirs(opts.outputPath)

    if opts.create_ublockorigin:
        # TODO: move this into the arguments
        uBlockFormats = {
            "google": 'google.com##a[href*="{url}"]:upward(2):remove()\n',
            "duckduckgo": 'duckduckgo.com##a[href*="{url}"]:upward(figure):upward(1):remove()\n',
            "bing": 'bing.com##a[href*="{url}"]:upward(li):remove()\n',
        }

        writtenFiles = []

        for name in uBlockFormats:
            # Get the target path for this subset of rules for this format
            targetPath = join(opts.outputPath, name + "-list_uBlockOrigin.txt")
            if exists(targetPath) and isfile(targetPath):
                remove(targetPath)
            elif isdir(targetPath):
                warnings.warn(f"Target path {targetPath} is a directory, skipping")
                continue
            
            # write all the formatted lines from the appropriate files
            with open(targetPath, "x") as file:

                for inputFile in commonFiles:
                    with open(inputFile, "r") as f:
                        while True:
                            headerLines, lines = __getLineList__.getLineList(f)
                            if (len(headerLines) == 0 and len(lines) == 0):
                                file.write('\n')
                                break
                            
                            file.writelines([formatLine(line, uBlockFormats[name], name) for line in headerLines + lines])

            
            writtenFiles.append(targetPath)

        # grab all the written files and add them together
        if opts.compile_ublockorigin:
            targetPath = join(opts.outputPath, "list_uBlockOrigin.txt")
            compileSuccess = compileFiles(writtenFiles, targetPath, "! Title: Huge AI Blocklist (Compiled)\n")

    if opts.create_ublacklist:
        # TODO: move this into the arguments
        uBlacklistFormat = '*://*.{url}/*\n'

        targetPath = join(opts.outputPath, "list_uBlacklist.txt")
        if isdir(targetPath):
            warnings.warn(f"Target path {targetPath} is a directory, skipping")
        else:
            if exists(targetPath) and isfile(targetPath):
                remove(targetPath)
            
            with open(targetPath, "x") as file:
                for inputFile in commonFiles:
                    with open(inputFile, "r") as f:
                        while True:
                            headerLines, lines = __getLineList__.getLineList(f)
                            if (len(headerLines) == 0 and len(lines) == 0):
                                file.write('\n')
                                break
                            
                            file.writelines([
                                formatLine(line, uBlacklistFormat, "uBlacklist", commentReplacement="#")
                                for line in headerLines + lines])

    pass

if __name__ == '__main__':
    main()