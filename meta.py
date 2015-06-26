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
#


"""TV metadata utility."""
__author__ = "darklion"
__version__ = "0.1"


# Import modules
import sys
from tvdb_api import Tvdb

tvdb = Tvdb(interactive=True, cache=True)

# Check arguments
if len(sys.argv) != 2:
    sys.stderr.write("%s: Must supply exactly one argument!\n" % ( __file__))
    sys.exit(1)

# Process arguments
seriesname = sys.argv[1]
show = tvdb[seriesname]
print show['seriesname'] + ":"
for key in show.data.keys():
    if key != 'seriesname':
        print "\t" + key + ": ",
	print show[key]

