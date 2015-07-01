#! /usr/bin/env python
# $Id$
# NAME
#	meta - display metadata for a tv show
# SYNTAX
#	meta <showname>
# DESCRIPTION
#	Prints details for a tv show from the TVDB site.
# AUTHOR
#	Peter Lyons
# IMPLEMENTATION
#	Use the tvdb_api module.
# GLOBALS
#	tvdb		database connection object
#


"""TV metadata utility."""
__title__ = "TVDB.com Query Utility"
__author__ = "darklion"
__version__ = "0.1.1"
# Version 0.1	Initial development
# Version 0.1.1	Cleanup for further development

# Import modules
import sys
from tvdb_api import Tvdb

# Check arguments
if len(sys.argv) != 2:
    sys.stderr.write("%s: Must supply exactly one argument!\n" % ( __file__))
    sys.exit(1)

# Connect to database
tvdb = Tvdb(interactive=True, cache=True)

# Process query
seriesname = sys.argv[1]
show = tvdb[seriesname]
print show['seriesname'] + ":"
for key in show.data.keys():
    if key != 'seriesname':
        print "\t" + key + ": ",
	print show[key]

