import optparse as opt
import warnings
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

def formatLine(line: str, format: str, engine: str, headerPrefix: str = "! //", commentPrefix = "!") -> str:
    if line.startswith(headerPrefix) or line.startswith(commentPrefix):
        return line.replace("{engine}", engine) + '\n'

    return format.replace("{url}", line.rstrip()) + '\n'

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
        warnings.warn(f"Output path {opts.outputPath} is a file, not a directiory")
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
                            if (len(lines) == 0 and len(headerLines) == 0):
                                file.write('\n')
                                break
                            
                            file.writelines([formatLine(line, uBlockFormats[name], name) for line in headerLines + lines])

            
            writtenFiles.append(targetPath)

        # grab all the written files and add them together
        if opts.compile_ublockorigin:
            targetPath = join(opts.outputPath, "list_uBlockOrigin.txt")
            if isdir(targetPath):
                warnings.warn(f"uBlockOrigin compiled path target {targetPath} is a folder, cancelling")
            elif exists(targetPath) and isfile(targetPath):
                remove(targetPath)
                compileFiles(writtenFiles, )
                with open(targetPath, "x") as targetFile:

                    for filename in writtenFiles:
                        if exists(filename) and isfile(filename):
                            with open(filename, "r") as f:
                                for line in f:
                                    targetFile.writelines(line)



    pass

if __name__ == '__main__':
    main()