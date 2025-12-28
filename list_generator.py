import optparse as opt
import warnings
import getLineList
from dataclasses import dataclass
from io import TextIOWrapper
from os import walk, makedirs, remove
from os.path import isfile, isdir, join, exists
from typing import overload

@dataclass
class FormatOptions:
    """
    :param str format: The format to place the line contents into. `{url}` in this string gets replaced with the line contents
    :param str engine: The engine that this line is being created for. Replaces `{engine}` in a string beginning with :param str headerPrefix: or :param str commentPrefix:
    :param str headerPrefix: The prefix expected for a commented header line
    :param str commentPrefix: The prefix expected for a commented line
    :param str commentReplacement: The string to replace the comment prefix with. Use when the engine doesn't use the default comment character (`!`)
    :param bool applyPrefix: 
    :param str linePrefixToApply:
    :param bool applySuffix:
    :param str lineSuffixToApply:

    :param bool hostsMode:
    """
    format: str
    engine: str
    headerPrefix: str = "! //"
    commentPrefix: str = "!"
    commentReplacement: str = "!"
    applyPrefix: bool = False
    linePrefixToApply: str = ""
    applySuffix: bool = False
    lineSuffixToApply: str = ""

    # extra handling for the hosts.txt format
    hostsMode: bool = False

def getOpts() -> opt.Values:
    parser = opt.OptionParser(
        description="Site blocklist generator script"
        )
    
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


    # Nuclear
    parser.add_option(
        "-n", "--nuclear", 
        action='store_true', dest='create_nuclear_list', default=True)
    

    # Folders
    parser.add_option(
        "--common-path",
        dest='commonPath', default="Common",)
    parser.add_option(
        "--subpage-path",
        dest='subpagePath', default="SubPages",)
    parser.add_option(
        "--nuclear-path",
        dest='nuclearPath', default="Nuclear",
        help='Path for the folder containing the nuclear option lists')
    parser.add_option(
        "--element-path",
        dest='elementPath', default="Elements",
        help='Path for the folder containing additional elements added to the uBlockOrigin list')


    # Export
    parser.add_option(
        "-o", "--output-folder",
        dest='outputPath', default="Export",
        help='')
    parser.add_option(
        "--overwrite",
        action='store_true', dest='overwrite', default=True,
        help='')

    opts, args = parser.parse_args()

    return opts

def formatLine(line: str, formatOptions: FormatOptions) -> str:
    """
    Format a line appropriately for the target engine & format

    :param str line: The contents of the line to be formatted
    :return: The formatted line according to `formatOptions`. Returns `formatOptions.format` if `{url}` is not present and `line` is not a comment
    """
    
    if line.startswith(formatOptions.headerPrefix) or line.startswith(formatOptions.commentPrefix):
        line = line.replace("{engine}", formatOptions.engine)
        line = line.replace(formatOptions.commentPrefix, formatOptions.commentReplacement, 1) # replace the comment character for other file types
        return line

    if line.rstrip() == "":
        return line
    
    if formatOptions.hostsMode:
        # remove leading periods
        # still continue to allow the www. prefix to be applied?
        line = line.strip(" .") 

        if line.__contains__("/"):
            # afaik the hosts format doesn't allow individual pages? still return the line commented though
            return "#       " + line
        

    if formatOptions.applyPrefix:
        if not line.startswith(formatOptions.linePrefixToApply):
            line = formatOptions.linePrefixToApply + line
    
    if formatOptions.applySuffix:
        line = line.rstrip()
        if not line.endswith(formatOptions.lineSuffixToApply):
            line = line + formatOptions.lineSuffixToApply
        line = line + "\n"

    format = formatOptions.format.rstrip() + "\n" # Normalise the format line ending, add if not present
    return format.replace("{url}", line.rstrip())

def getFiles(folder: str) -> list[str]:
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
def getFiles_Sorted(folder: str) -> list[str]: ...
@overload
def getFiles_Sorted(files: list[str]) -> list[str]: ...

def getFiles_Sorted(input) -> list[str]:
    #print(type(input), input)
    if type(input) == str:
        files = getFiles(input)
        return sorted(files, key=str.lower)
    if type(input) == list[str]:
        return sorted(input, key=str.lower)


def writeFormattedLinesToFile(inputFilePaths: list[str], outputFile: TextIOWrapper, formatOptions: FormatOptions):

    # write all the formatted lines from the appropriate files
    lineConfig = getLineList.LineConfig(expandDomains=True)

    for inputFile in inputFilePaths:
        if isfile(inputFile):
            with open(inputFile, "r") as f:
                while True:
                    headerLines, lines = getLineList.getLineList(f, lineConfig)
                    if (len(headerLines) == 0 and len(lines) == 0):
                        outputFile.write('\n')
                        break
                    
                    outputFile.writelines([
                        formatLine(line, formatOptions)
                        for line in headerLines + lines
                    ])

                    outputFile.write("\n")

def tryWriteToPath(path: str, inputFilePaths: list[str], formatOptions: FormatOptions, overwrite: bool = True) -> bool:
    
    if exists(path) and isfile(path):
        if overwrite:
            remove(path)
        else:
            warnings.warn(f"Target file exists and overwriting is disabled, skipping")
            return False
        
    elif isdir(path):
        warnings.warn(f"Target file {path} is a directory, skipping")
        return False

    with open(path, "x") as f:
        writeFormattedLinesToFile(inputFilePaths, f, formatOptions)
        print(f"Successfully wrote {path}")
        return True

def compileFiles(inputFilePaths: list[str], outputFile: str, outputHeader: str, overwrite: bool = True) -> bool:
    if exists(outputFile):
        if isdir(outputFile):
            warnings.warn(f"Targeted path {outputFile} is a directory, cancelling writing from {inputFilePaths}")
            return False
            
        if overwrite:
            remove(outputFile)
        else:
            warnings.warn(f"Target file exists and overwriting is disabled, skipping")
            return False
    
    with open(outputFile, "x") as f:
        f.write(outputHeader+'\n')
        for path in inputFilePaths:
            if isfile(path):
                with open(path, "r") as inputFile:
                    for line in inputFile:
                        f.write(line)
                    
                    f.write('\n')
    
    print(f"Successfully compiled {outputFile}")
    return True

def main():
    opts = getOpts()
    #print(opts)
    
    commonFiles = getFiles_Sorted(opts.commonPath)
    subpageFiles = getFiles_Sorted(opts.subpagePath)
    nuclearFiles = getFiles_Sorted(opts.nuclearPath)
    elementFiles = getFiles_Sorted(opts.elementPath)

    if isfile(opts.outputPath):
        warnings.warn(f"Output path {opts.outputPath} is a file, not a directiory. Cancelling compilation")
        return
    elif not exists(opts.outputPath):
        makedirs(opts.outputPath)

    if opts.create_ublockorigin:
        # TODO: move this into the arguments
        uBlockFormats = {
            "google": 'google.com##a[href*="{url}"]:upward(2):remove()',
            "duckduckgo": 'duckduckgo.com##a[href*="{url}"]:upward(figure):upward(1):remove()',
            "bing": 'bing.com##a[href*="{url}"]:upward(li):remove()',
        }

        writtenFiles = []
        writtenFiles_Nuclear = []

        for engine in uBlockFormats:
            
            lineFormat = FormatOptions(
                format=uBlockFormats[engine],
                engine=engine,
            )

            targetPath = join(opts.outputPath, lineFormat.engine + "-list_uBlockOrigin.txt")
            
            wasFileWritten = tryWriteToPath(targetPath, commonFiles + subpageFiles, lineFormat, opts.overwrite)

            if wasFileWritten:
                writtenFiles.append(targetPath)

        if opts.create_nuclear_list:

            for engine in uBlockFormats:
                lineFormat = FormatOptions(
                    format=uBlockFormats[engine],
                    engine=engine + " (Nuclear)"
                )

                targetPath = join(opts.outputPath, "Nuclear_" + engine + "-list_uBlockOrigin.txt")

                wasFileWritten = tryWriteToPath(targetPath, nuclearFiles, lineFormat, opts.overwrite)

                if wasFileWritten:
                    writtenFiles_Nuclear.append(targetPath)

        # grab all the written files and add them together
        if opts.compile_ublockorigin:
            targetPath = join(opts.outputPath, "list_uBlockOrigin.txt")
            compileFiles(writtenFiles, targetPath, "! Title: Huge AI Blocklist (Compiled)\n", opts.overwrite)

            if opts.create_nuclear_list:
                targetPath = join(opts.outputPath, "Nuclear_list_uBlockOrigin.txt")
                compileFiles(writtenFiles, targetPath, "! Title: Huge AI Blocklist (Nuclear) (Compiled)\n", opts.overwrite)

    if opts.create_ublacklist:
        # TODO: move this into the arguments
        uBlacklistFormat = FormatOptions(
            # Need to discuss 
            format='*://*{url}*',
            engine="uBlacklist",
            commentReplacement="#",
            applyPrefix=True,
            linePrefixToApply=".",
            applySuffix=True,
            lineSuffixToApply="/"
            )

        targetPath = join(opts.outputPath, "list_uBlacklist.txt")

        wasFileWritten = tryWriteToPath(targetPath, commonFiles + subpageFiles, uBlacklistFormat, opts.overwrite)

        if opts.create_nuclear_list:
            targetPath = join(opts.outputPath, "Nuclear_list_uBlacklist.txt")

            wasFileWritten = tryWriteToPath(targetPath, nuclearFiles, uBlacklistFormat, opts.overwrite)

    if opts.create_hosts:
        hostsFormats = [
            FormatOptions(
                format='0.0.0.0 {url}',
                engine='hosts',
                commentReplacement="#",
                hostsMode=True
            ),
            FormatOptions(
                format='0.0.0.0 www{url}',
                engine='hosts-www',
                commentReplacement="#",
                applyPrefix=True,
                linePrefixToApply='.',
                hostsMode=True
            )
        ]

        writtenFiles = []

        for format in hostsFormats:
            targetPath = join(opts.outputPath, format.engine + ".txt")

            wasFileWritten = tryWriteToPath(targetPath, commonFiles, format, opts.overwrite)
            if wasFileWritten:
                writtenFiles.append(targetPath)
        
        if opts.compile_hosts:
            targetPath = join(opts.outputPath, "list_hosts.txt")
            compileFiles(writtenFiles, targetPath, "# Title: Huge AI Blocklist (Compiled)\n", opts.overwrite)


if __name__ == '__main__':
    main()