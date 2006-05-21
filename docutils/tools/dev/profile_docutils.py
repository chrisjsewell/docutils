#!/usr/bin/python -i

# $Id$
# Author: Felix Wiemann <Felix.Wiemann@ososo.de>
# Copyright: This script has been placed in the public domain.

import os.path
import docutils.core
import hotshot.stats

print 'Profiler started.'

os.chdir(os.path.join(os.path.dirname(docutils.__file__), '..'))

print 'Profiling...'

prof = hotshot.Profile('docutils.prof')
prof.runcall(docutils.core.publish_file, source_path='HISTORY.txt',
             destination_path='prof.HISTORY.html', writer_name='html')
prof.close()

print 'Loading statistics...'

print """
stats = hotshot.stats.load('docutils.prof')
stats.strip_dirs()
stats.sort_stats('time')  # 'cumulative'; 'calls'
stats.print_stats(40)
"""

stats = hotshot.stats.load('docutils.prof')
stats.strip_dirs()
stats.sort_stats('time')
stats.print_stats(40)

try:
    execfile(os.environ['PYTHONSTARTUP'])
except:
    pass
