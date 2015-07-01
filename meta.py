#! /usr/bin/env python
# $Id$
# NAME
#	meta - display metadata for a tv show
# SYNTAX
#	meta [-dhiuv] <showname>
# DESCRIPTION
#	Prints details for a tv show from the TVDB site.
# OPTIONS
#	-d, --debug		Show debugging info.
#	-h, --help		Display help message.
#	-i, --interactive	Activate tvdb_api interactive mode.
#	-u, --usage		Display examples for executing the meta script.
#	-v, --version		Display version and author.
# AUTHOR
#	Peter Lyons
# IMPLEMENTATION
#	Use the tvdb_api module.
# GLOBALS
#	tvdb		database connection object
#	usage_description	initial usage text - basic summary
#	usage_examples		ending usage text - contains command examples
#	opts		parsed options information
#	opts.debug		print debugging info?
#	opts.interactive	invoke tvdb_api using interactively?
#	opts.usage		print usage info?
#	opts.version		print version and author info?
#


"""TV metadata utility."""
__title__ = "TVDB.com Query Utility"
__author__ = "darklion"
__version__ = "0.1.2"
# Version 0.1	Initial development
# Version 0.1.1	Cleanup for further development
# Version 0.1.2	Define some basic options & usage info

usage_description = '''
This script fetches TV series information from TheTVDB.com web site.

'''
usage_examples = '''
Command example:
# Print all the show information for a series:
> meta "Doctor Who"
TVDB Search Results:
1 -> Doctor Who [en] # http://thetvdb.com/?tab=series&id=76107&lid=7 (default)
2 -> Totally Doctor Who [en] # http://thetvdb.com/?tab=series&id=80160&lid=7
3 -> Doctor Who Greatest Moments [en] # http://thetvdb.com/?tab=series&id=110141&lid=7
4 -> Doctor Who - Fan Created Series [en] # http://thetvdb.com/?tab=series&id=282314&lid=7
5 -> Doctor Who (2009) [en] # http://thetvdb.com/?tab=series&id=112671&lid=7
6 -> Doctor Who (2005) [en] # http://thetvdb.com/?tab=series&id=78804&lid=7
Enter choice (first number, return for default, 'all', ? for help): 1
Doctor Who:
	networkid:  None
	rating:  9.4
	airs_dayofweek:  Saturday
	contentrating:  TV-PG
	id:  76107
	airs_time:  5:15 PM
	network:  BBC One
	fanart:  http://thetvdb.com/banners/fanart/original/76107-23.jpg
	lastupdated:  1434679247
	actors:  |William Hartnell|Patrick Troughton|Jon Pertwee|Tom Baker|Sylvester McCoy|Peter Davison|Paul McGann|Richard Hurndall|Colin Baker|Sarah Sutton|Elisabeth Sladen|William Russell|Jacqueline Hill|Carole Ann Ford|Maureen O'Brien|Mark Strickson|Bonnie Langford|Mary Tamm|Nicola Bryant|Caroline John|Louise Jameson|Katy Manning|Janet Fielding|Lalla Ward|Deborah Watling|Eric Roberts|Daphne Ashbrook|Sophie Aldred|Anthony Ainley|Geoffrey Beevers|Peter Pratt|Roger Delgado|
	ratingcount:  147
	status:  Ended
	added:  None
	poster:  http://thetvdb.com/banners/posters/76107-4.jpg
	tms_wanted_old:  1
	imdb_id:  tt0056751
	genre:  |Action|Adventure|Science-Fiction|
	banner:  http://thetvdb.com/banners/graphical/76107-g14.jpg
	seriesid:  355
	language:  en
	zap2it_id:  SH001301
	addedby:  None
	firstaired:  1963-11-23
	runtime:  25
	overview:  Doctor Who is the longest-running science fiction TV series in history, airing initially from 1963 to 1989.  Doctor Who is about ideas.  It pioneered sophisticated mixed-level storytelling. Its format was the key to its longevity: the Doctor, a mysterious traveller in space and time, travels in his ship, the TARDIS.  The TARDIS can take him and his companions anywhere in time and space. Inevitably he finds evil at work wherever he goes...
'''

# System modules
import sys
from optparse import OptionParser

# Database modules
from tvdb_api import Tvdb

# Process arguments
parser = OptionParser(usage=u"%prog -dhiuv <seriesname>")
parser.add_option( "-d", "--debug", action="store_true", default=False,
                   dest="debug",
                   help=u"Show debugging info")
parser.add_option( "-i", "--interactive", action="store_true", default=False,
                   dest="interactive",
                   help=u"Activate the tvdb_api interactive mode\n(allows prompted selection from matching series")
parser.add_option( "-u", "--usage", action="store_true", default=False,
                   dest="usage",
                   help=u"Display examples for executing the meta script")
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

# Check for required argument
if len(args) != 1:
    sys.stderr.write("%s: Must supply exactly one argument!\n" % ( __file__))
    sys.exit(1)

# Connect to database
tvdb = Tvdb(interactive=opts.interactive, cache=True)

# Process query
seriesname = args[0]
show = tvdb[seriesname]
print show['seriesname'] + ":"
for key in show.data.keys():
    if key != 'seriesname':
        print "\t" + key + ": ",
	print show[key]

