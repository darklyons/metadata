#! /usr/bin/env python
# $Id$
# NAME
#	shown - display AU broadcast date for tv shows
# SYNTAX
#	shown <episode-metadata-files>
# DESCRIPTION
#	Displays the local broadcast date for tv show metadata files given.
#	It estimates missing information from the supplied corpus of data.
# OPTIONS
#	-d, --debug		Show debugging info.
#	-h, --help		Display help message.
#	-t TARGET, --target=TARGET
#				Code for locality to display (default: AU).
#	-u, --usage		Display examples for executing the shown script.
#	-v, --version		Display version and author.
# AUTHOR
#	Peter Lyons
# IMPLEMENTATION
# GLOBALS
#	usage_description	initial usage text - basic summary
#	usage_examples		ending usage text - contains command examples
#	opts		parsed options information
#	opts.debug		print debugging info?
#	opts.usage		print usage info?
#	opts.version		print version and author info?
#


"""Show TV episodes AU broadcast dates."""
__title__ = "Broadcast Date Display Utility"
__author__ = "darklion"
__version__ = "0.1.2"
# Version 0.1	Initial development skeleton
# Version 0.1.1	Basic metadata processing with no actual estimating
# Version 0.1.2	Make source and target of the estimating variable

usage_description = '''
This script displays TV Show Broadcast Dates using data from the supplied files.

'''
usage_examples = '''
Command examples:
> shown /images/media/Doctor\ Who/Season\ 198*/.*.meta
> shown -t AU /images/media/*/Season\ 1987.*/.*.meta
'''

# System modules
import sys
from optparse import OptionParser


def ParseMeta(filename):
    '''Extract metadata date information from the file.'''
    file = open(filename, 'r')
    # Build metadata object
    info = {}
    for line in file:
	line = line.replace('\n', '')
        record = line.split(':')
        (value, tag) = (record[0], record[1])
        info[tag] = value
    file.close
    return info


def Estimate(source, target, meta):
    '''Estimate any missing AU broadcast data.'''
    for key in meta:
	info = meta[key]
        if target not in info:
            info[target] = info[source]
    return meta


# Main program
def main():
# Init globals
    SOURCE = 'broadcast'

# Process arguments
    parser = OptionParser(usage=u"%prog -dhtuv <metadata-filenames>]")
    parser.add_option( "-d", "--debug", action="store_true", default=False,
                       dest="debug",
                       help=u"Show debugging info")
    parser.add_option( "-t", "--target", metavar="TARGET", default='AU',
                       dest="target",
                       help=u"Target locality code for estimating")
    parser.add_option( "-u", "--usage", action="store_true", default=False,
                       dest="usage",
                       help=u"Display examples for executing the shown script")
    parser.add_option( "-v", "--version", action="store_true", default=False,
                       dest="version",
                       help=u"Display version and author")
    (opts, args) = parser.parse_args()

# Output debugging info?
    if opts.debug == True:
        print "opts", opts
        print "\nargs", args

# Output version info & terminate?
    if opts.version == True:
        sys.stdout.write("%s - %s (%s) by %s\n" %
                         (__file__, __title__, __version__, __author__ ))
        sys.exit(0)

# Output usage info & terminate?
    if opts.usage == True:
        sys.stdout.write(usage_description)
        parser.print_usage()
        sys.stdout.write(usage_examples)
        sys.exit(0)

# Check for required arguments
    if len(args) == 0:
        parser.error("Must supply at least one metadata file name!")
        sys.exit(1)

# Process file info
    meta = {}
    for filename in args:
        info = ParseMeta(filename)
	meta[filename] = info

# Estimate missing info
    meta = Estimate(SOURCE, opts.target, meta)

# Output info
    for filename in meta:
        print filename + ':',
        print meta[filename][opts.target]

# Finished
    sys.exit(0)
#end main

if __name__ == "__main__":
    main()
