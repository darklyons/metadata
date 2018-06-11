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
#	-M YYYY-MM-DD, --metadate=YYYY-MM-DD
#				maximum date allowed for '.meta' files,
#				otherwise use backup versions (default: none).
#	-o, --override		Override approximate dates with their estimate
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
#	opts.override		override approximate dates with an estimate?
#	opts.usage		print usage info?
#	opts.version		print version and author info?
#


"""Show TV episodes AU broadcast dates."""
__title__ = "Broadcast Date Display Utility"
__author__ = "darklion"
__version__ = "0.5.2"
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
# Version 0.2.9	Handle an optional time when parsing dates
# Version 0.3.0	Prep to calculate an estimate if the target date is approximate
# Version 0.3.1	Continue prep by saving the estimate as a separate attribute
# Version 0.4.1	Optionally filter metadata files by modification date
# Version 0.4.2	Modification date filtering should be able to eliminate an entry
# Version 0.5.0	Allow override of approximate dates with estimate (first cut)
# Version 0.5.1	When overriding, only report on dates with values/estimates
# Version 0.5.2	Bug fixes: find latest file when metadate set and handle bad tag values

usage_description = '''
This script displays TV Show Broadcast Dates using data from the supplied files.

'''
usage_examples = '''
Command examples:
> shown data/Season\ 198*/.*.meta
> shown -t AU data/Season\ 1987.*/.*.meta
'''

# System modules
import os
import sys
from datetime import date, datetime, timedelta
from optparse import OptionParser


class ExtDate(date):
    ''' Wraps Date class to allow for extra attributes.'''


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
    isEstimate = False
    if not month.isdigit():
        match = monthdict.get(month, None)
        if match is None:
            month = '06'
            day   = '30'
        else:
            month = match
        isEstimate = True
    if not day.isdigit():
        match = daydict.get(day, None)
        if match is None:
            day   = '15'
        else:
            day   = match
        isEstimate = True
    try:
        match = ExtDate(int(year), int(month), int(day))
        match.isEstimate = isEstimate
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
                if tag.isalpha() and value is not None:
                    info[tag] = value
                elif tag.isalpha():
                    sys.stderr.write('Bad value for tag "'+tag+'" in '+filename+'\n')
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
    global opts
    tree = InitDelta(source, target, meta)
    for key in meta:
        info = meta[key]
        if target not in info:
            delta = CalcDelta(key, tree)
            estimate = info.get(source, None)
            if estimate is not None:
                estimate += delta
            info['TARGET'] = estimate
            info['DELTA'] = delta
        elif opts.override and info[target].isEstimate:
            delta = CalcDelta(key, tree)
            estimate = info.get(source, None)
            if estimate is not None:
                estimate += delta
            info['TARGET'] = estimate
            info['DELTA'] = delta
        else:
            info['TARGET'] = info[target]
    return meta


# Main program
def main():
# Init globals
    global opts
    SOURCE = 'broadcast'

# Process arguments
    parser = OptionParser(usage=u"%prog -dhouv [-M <metadate-limit>] [-t <target>] <metadata-filenames>]")
    parser.add_option( "-d", "--debug", action="store_true", default=False,
                       dest="debug",
                       help=u"Show debugging info")
    parser.add_option( "-M", "--metadate", metavar="METADATE", default=False,
                       dest="metadate",
                       help=u"Maximum modify date for metadata files")
    parser.add_option( "-o", "--override", action="store_true", default=False,
                       dest="override",
                       help=u"Override approximate dates with an estimate")
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

# Convert metadate to a date?
    if opts.metadate:
        opts.metadate = ParseDate(opts.metadate)
        if opts.metadate:
            opts.metadate = datetime.combine(opts.metadate, datetime.min.time())

# Create file list
    meta = {}
    for path in args:
        if not os.path.isdir(path):
            meta[path] = {}
        else:
            for dirpath, dirs, files in os.walk(path):
                oldname = False
                startname = False
                for name in sorted(files):
                    fullname = os.path.join(dirpath, name)
                    mtime = os.path.getmtime(fullname)
                    mdate = datetime.fromtimestamp(mtime)
                    if name.endswith('.meta'):
                    # Normal case - check against metadate
                        if oldname:
                        # Finish off abnormal case handling
                            meta[oldname] = {}
                            oldname = False
                        if opts.metadate and mdate > opts.metadate:
                        # Problem with normal - look for older version
                            startname = name
                        else:
                        # Normal case is okay
                            startname = False
                            meta[fullname] = {}
                    elif startname and name.startswith(startname):
                    # Abnormal - stop when metadate checks out (or fall thru)
                        if mdate <= opts.metadate:
                            oldname = fullname
            # Finish outstanding abnormal case
                if oldname:
                    meta[oldname] = {}

# Extract file info
    for filename in meta:
        if opts.debug == True:
            sys.stderr.write(filename+'\n')
        info = ParseMeta(filename)
        if opts.override and opts.target not in info:
            pass
        else:
            meta[filename] = info

# Estimate missing info
    meta = Estimate(opts.source, opts.target, meta)

# Output info
    for filename in meta:
        if opts.debug != True:
            print "%s:%s" % (filename, meta[filename]['TARGET'])
        else: 
            print "%s:%s" % (filename, meta[filename]['TARGET']),
            print meta[filename].get('DELTA', None)

# Finished
    sys.exit(0)
#end main

if __name__ == "__main__":
    main()
