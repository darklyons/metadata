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
__version__ = "0.2.0"
# Version 0.1	Initial development skeleton
# Version 0.1.1	Basic metadata processing with no actual estimating
# Version 0.1.2	Make source and target of the estimating variable
# Version 0.1.3	Introduce perfunctory date parsing on the input metadata
# Version 0.1.4	Handle missing and malformed metadata edge cases
# Version 0.1.5	Extend the depth of the date parsing for the input metadata
# Version 0.2.0	Start using the system date routines in preparation for estimating

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
from datetime import date, timedelta
from optparse import OptionParser


def ParseDate(value):
    '''Extract a legitimate date from the generalized date string.'''
# Init missing parts lookup
    monthdict = {'0?': '05', '1?': '11'}
    daydict   = {'??': '15', '0?': '05', '1?': '15', '2?': '25', '3?': '30'}
# Get three parts of the date
    parts = value.split('-')
    while len(parts) < 3:
        parts.append('')
    [year, month, day] = parts
# Handle missing parts
    if not month.isdigit():
        match = monthdict.get(month, None)
        if match is None:
            month = '06'
            day   = '30'
        else:
            month = match
    if not day.isdigit():
        match = daydict.get(day, None)
        if match is None:
            day   = '15'
        else:
            day   = match
    try:
        match = date(int(year), int(month), int(day))
    except:
        print value+'='+parts
        match = None
    return match


def ParseMeta(filename):
    '''Extract metadata date information from the file.'''
    file = open(filename, 'r')
    # Build metadata object
    info = {}
    for line in file:
	line = line.replace('\n', '')
        record = line.split(':')
	if len(record) > 1:
            (value, tag) = (record[0], record[1])
            info[tag] = ParseDate(value)
    file.close
    return info


def InitDelta(source, target, meta):
    '''Create an empty tree structure for later use in estimating dates from file metadata.'''
    tree = {}
    return tree


def CalcDelta(source, target, tree):
    '''Estimate a zero date delta from the tree.'''
    delta = timedelta(0)
    return delta


def Estimate(source, target, meta):
    '''Estimate any missing target broadcast data.'''
    tree = InitDelta(source, target, meta)
    for key in meta:
	info = meta[key]
        if target not in info:
            delta = CalcDelta(source, target, tree)
            estimate = info.get(source, None)
            if estimate is not None:
                estimate += delta
            info[target] = estimate
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
