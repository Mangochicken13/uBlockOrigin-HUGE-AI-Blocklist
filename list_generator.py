import optparse as opt
import warnings
from os import walk, path
from os.path import isfile, isdir, join


def getOpts() -> opt.Values:
    parser = opt.OptionParser(
        description="Site blocklist generator script"
        )

    parser.add_option(
        "--hosts",
        action='store_true', dest='create_hosts', default=True,
        help='Enable hosts.txt file creation (default)')
    parser.add_option(
        "--no-hosts",
        action='store_false', dest='create_hosts',
        help='Disable all hosts file creation. Includes --no-compile-hosts')
    parser.add_option(
        "--compile-hosts",
        action='store_true', dest='compile_hosts', default=True,
        help='Compile all hosts formats (default)')
    parser.add_option(
        "--no-compile-hosts",
        action='store_false', dest='compile_hosts',
        help="Don't compile the hosts.txt formats together")

    parser.add_option(
        "--ublacklist",
        action='store_true', dest='create_ublacklist', default=True,
        help='Create uBlacklist file format (default)')
    parser.add_option(
        "--no-ublacklist", 
        action='store_false', dest='create_ublacklist',
        help="Don't create uBlacklist file format")

    parser.add_option(
        "--ublockorigin", "--ubo", "--ublock",
        action='store_true', dest='create_ublockorigin', default=True,
        help='Create uBlockOrigin file (default)')
    parser.add_option(
        "--no-ublockorigin", "--no-ubo", "--no-ublock",
        action='store_false', dest='create_ublockorigin',
        help='Disable all uBlockOrigin file creation. Includes --no-compile-ublockorigin')
    parser.add_option(
        "--compile-ublockorigin", "--compile-ubo", "--compile-ublock",
        action='store_true', dest='compile_ublockorigin', default=True,
        help='Compile all uBlockOrigin formats (default)')
    parser.add_option(
        "--no-compile-ublockorigin", "--no-compile-ubo", "--no-compile-ublock",
        action='store_false', dest='compile_ublockorigin',
        help="Don't compile the uBlockOrigin formats together")

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

    opts, args = parser.parse_args()

    return opts

def main():
    opts = getOpts()
    #print(opts)

    
    commonFiles = []
    if isdir(opts.commonPath):
        commonFiles.extend([join(dirpath, f) for (dirpath, dirnames, filenames) in walk(opts.commonPath) for f in filenames])
    else:
        if isfile(opts.commonPath):
            warnings.warn(f"--common-path '{opts.commonPath}' is a file, proceeding with only {opts.commonPath} in the common file list")
            commonFiles.append(opts.commonPath)
        else:
            warnings.warn(f"--common-path '{opts.commonPath}' is not a file or dir, proceeding with no common files")
    print(commonFiles, "\n")
    
    nuclearFiles = []
    if isdir(opts.nuclearPath):
        nuclearFiles.extend([join(dirpath, f) for (dirpath, dirnames, filenames) in walk(opts.nuclearPath) for f in filenames])
    else:
        if isfile(opts.nuclearPath):
            warnings.warn(f"--nuclear-path '{opts.nuclearPath}' is a file, proceeding with only {opts.nuclearPath} in the nuclear file list")
            nuclearFiles.append(opts.nuclearPath)
        else:
            warnings.warn(f"--nuclear-path '{opts.nuclearPath}' is not a file or dir, proceeding with no nuclear files")
    print(nuclearFiles, "\n")

    elementFiles = []
    if isdir(opts.elementPath):
        elementFiles.extend([join(dirpath, f) for (dirpath, dirnames, filenames) in walk(opts.elementPath) for f in filenames])
    else:
        if isfile(opts.elementPath):
            warnings.warn(f"--nuclear-path '{opts.elementPath}' is a file, proceeding with only {opts.elementPath} in the nuclear file list")
            elementFiles.append(opts.elementPath)
        else:
            warnings.warn(f"--nuclear-path '{opts.elementPath}' is not a file or dir, proceeding with no nuclear files")
    print(elementFiles, "\n")

    if opts.create_ublockorigin:
        print("helo!")

        pass

    pass

if __name__ == '__main__':
    main()