#! /usr/bin/env python
# $Id$
# NAME
#	shown - display AU broadcast date for tv shows
# SYNTAX
#	shown <episode-metadata-paths...>
# DESCRIPTION
#	Displays the local broadcast date for tv show metadata files given.
#	For directories, it processes all '.meta' files in the hierarchy.
#	It estimates missing information from the supplied corpus of data,
#	using differences calculated from files with both source & target data.
#	By default it estimates AU date based upon generic broadcast date.
# OPTIONS
#	-d, --debug		Show debugging info.
#	-h, --help		Display help message.
#	-s SOURCE, --source=SOURCE
#				Code to use as base (default: broadcast).
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
__version__ = "0.2.9"
# Version 0.1	Initial development skeleton
# Version 0.1.1	Basic metadata processing with no actual estimating
# Version 0.1.2	Make source and target of the estimating variable
# Version 0.1.3	Introduce perfunctory date parsing on the input metadata
# Version 0.1.4	Handle missing and malformed metadata edge cases
# Version 0.1.5	Extend the depth of the date parsing for the input metadata
# Version 0.2.0	Start using the system date routines in preparation for estimating
# Version 0.2.1	Calculate and use average time deltas using the metadata tree
# Version 0.2.2	Report the delta when debugging used as well as the estimate
# Version 0.2.3	Fix missing/erroneous documentation
# Version 0.2.4	Extend the cases handled by the metadata parsing
# Version 0.2.5	Process whole directory hierarchies if needed & some clean up
# Version 0.2.6	Allow use of different source (other than generic broadcast)
# Version 0.2.7	Extend metadata format to specialize tags (ie: "broadcast|US")
# Version 0.2.8	Buglet in except clause for ParseDate
# Versionf0.2.9	Handle an optional time when parsing dates

usage_description = '''
This script displays TV Show Broadcast Dates using data from the supplied files.

'''
usage_examples = '''
Command examples:
> shown /images/media/Doctor\ Who/Season\ 198*/.*.meta
> shown -t AU /images/media/*/Season\ 1987.*/.*.meta
'''

# System modules
import os
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
# Check for optional time
    daytime = day.split('@')
    if len(daytime) > 1:
        (day, time) = (daytime[0], daytime[1])
        parts[-1:] = daytime
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
        print value+'='+str(parts)
        match = None
    return match


def ParseMeta(filename):
    '''Extract metadata date information from the file.'''
    file = open(filename, 'r')
    # Build metadata object
    info = {}
    for line in file:
        line = line.rstrip()
        record = line.split(':')
        if len(record) > 1:
            pos = 0
            if record[0].isalpha():
                taglist = [record[0]]
                pos = 1
            elif record[1].isalpha():
                taglist = [record[1]]
            elif record[0].find('|') >= 0:
                taglist = record[0].split('|')
                pos = 1
            else:
                taglist = record[1].split('|')
            value = ParseDate(record[pos])
            for tag in taglist:
                if tag.isalpha():
                    info[tag] = value
                else:
                    sys.stderr.write('Bad tag "'+tag+'" in '+filename+'\n')
    file.close
    return info


def InitDelta(source, target, meta):
    '''Create a tree structure of all the date deltas from the file metadata.'''
    tree = {}
    for key in meta:
        info = meta[key]
        if source in info and target in info:
            delta = info[target] - info[source]
        # Get path elements and remove null root element
            path = key.split('/')
            if len(path[0]) == 0:
                path.pop(0)
        # Unwind the path to create the tree
            node = tree
            leaf = path.pop()
            for element in path:
                if element not in node:
                    node[element] = {}
                node = node[element]
        # Now at the tip of the tree
            node[leaf] = delta
    return tree


def SumLeaves(tree):
    '''Calculate the sum and count for all leaf values of the tree.'''
    sum  = timedelta(0)
    count = 0
    for key in tree:
        if isinstance(tree[key], dict):
            (treesum, treecount) = SumLeaves(tree[key])
            sum   += treesum
            count += treecount
        else:
            sum   += tree[key]
            count += 1
    return (sum, count)


def Average(path, tree):
    '''Calculate the average of the leaves at the deepest extent of the path
       that has values to be averaged.
    '''
# Start backup up if we reach the tip of the tree
# - by getting to the end of the path
    if len(path) == 0:
        return None
# - or running out of tree
    element = path.pop(0)
    if element not in tree:
        return None
# Otherwise descend the tree
    average = Average(path, tree[element])
# And calc an average if necessary
    if average is None:
        (sum, count) = SumLeaves(tree[element])
        if count > 0:
        # - and possible
            average = sum / count
    return average


def CalcDelta(key, tree):
    '''Estimate a date delta by comparing dates in the filename tree.'''
# Get path elements and remove null root element
    path = key.split('/')
    if len(path[0]) == 0:
        path.pop(0)
# Start the averaging one level up
    path.pop()
    delta = Average(path, tree)
    return delta


def Estimate(source, target, meta):
    '''Estimate any missing target broadcast data.'''
    tree = InitDelta(source, target, meta)
    for key in meta:
        info = meta[key]
        if target not in info:
            delta = CalcDelta(key, tree)
            estimate = info.get(source, None)
            if estimate is not None:
                estimate += delta
            info[target] = estimate
            info['DELTA'] = delta
    return meta


# Main program
def main():
# Init globals
    SOURCE = 'broadcast'

# Process arguments
    parser = OptionParser(usage=u"%prog -dhuv [-t <target>] <metadata-filenames>]")
    parser.add_option( "-d", "--debug", action="store_true", default=False,
                       dest="debug",
                       help=u"Show debugging info")
    parser.add_option( "-s", "--source", metavar="SOURCE", default='broadcast',
                       dest="source",
                       help=u"Source locality code for estimating")
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

# Create file list
    meta = {}
    for path in args:
        if not os.path.isdir(path):
            meta[path] = {}
        else:
            for dirpath, dirs, files in os.walk(path):
                for name in files:
                    if name.endswith('.meta'):
                        meta[os.path.join(dirpath, name)] = {}

# Extract file info
    for filename in meta:
        if opts.debug == True:
            sys.stderr.write(filename+'\n')
        info = ParseMeta(filename)
        meta[filename] = info

# Estimate missing info
    meta = Estimate(opts.source, opts.target, meta)

# Output info
    for filename in meta:
        if opts.debug != True:
            print "%s:%s" % (filename, meta[filename][opts.target])
        else: 
            print "%s:%s" % (filename, meta[filename][opts.target]),
            print meta[filename].get('DELTA', None)

# Finished
    sys.exit(0)
#end main

if __name__ == "__main__":
    main()
