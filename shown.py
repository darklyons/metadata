#! /usr/bin/env python
# $Id$
# NAME
#	shown - display AU broadcast date for tv shows
# SYNTAX
#	shown <episode-metadata-files>
# DESCRIPTION
#	Displays the AU broadcast date for tv show metadata files given.
#	It estimates missing information from the supplied corpus of data.
# OPTIONS
#	-d, --debug		Show debugging info.
#	-h, --help		Display help message.
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
__version__ = "0.1"
# Version 0.1	Initial development skeleton

usage_description = '''
This script displays TV Show Broadcast Dates using data from the supplied files.

'''
usage_examples = '''
Command examples:
> shown /images/media/Doctor\ Who/Season\ 198*/.*.meta
> shown /images/media/*/Season\ 1987.*/.*.meta
'''

# System modules
import sys
from optparse import OptionParser

def main():
# Process arguments
    parser = OptionParser(usage=u"%prog -dhuv <metadata-filenames>]")
    parser.add_option( "-d", "--debug", action="store_true", default=False,
                       dest="debug",
                       help=u"Show debugging info")
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

# Process query
    print args
# Finished
    sys.exit(0)
#end main

if __name__ == "__main__":
    main()
