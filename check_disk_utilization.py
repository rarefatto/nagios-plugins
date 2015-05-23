#!/usr/bin/python

"""Nagios/Icinga plugin to check filesystem usage."""

import argparse
import logging
import nagiosplugin
import subprocess
import os

_log = logging.getLogger('nagiosplugin')


# data acquisition

class FilesystemUsagePercentage(nagiosplugin.Resource):
    """Domain model: filesystem usage percentage.
    Determines the filesystem usage percentage
    """
    def probe(self):
        _log.info('reading data from df')
        
        df_output_lines = [s.split() for s in os.popen("df -Ph").read().splitlines()]        
        _log.debug('df_output_lines %s', df_output_lines)
        _log.debug('range %s', range(1,len(df_output_lines)))        
        for i in range(1,len(df_output_lines)):
            _log.debug('Filesystem %s %s' % (df_output_lines[i][5],df_output_lines[i][4][:-1]) )        
            yield nagiosplugin.Metric('Usage %s' % df_output_lines[i][5], float(df_output_lines[i][4][:-1]), min=0,
                                      context='FilesystemUsagePercentage')

class FilesystemUsageSummary(nagiosplugin.Summary):

    def verbose(self, results):
        ''' Super-classes summary so we can get verbose results '''
        super(FilesystemUsageSummary, self).verbose(results)


    def ok(self, results):
        return "[" + "][".join(
                        "%s = %s (State= %s)" % (x.metric.name,x.metric,x.state) 
                        for x in results
                        ) + "]"

    def problem(self, results):
        return self.ok( results)
    
@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-w', '--warning', metavar='RANGE', default='',
                      help='return warning if load is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='',
                      help='return critical if load is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        FilesystemUsagePercentage(),\
        nagiosplugin.ScalarContext('FilesystemUsagePercentage',args.warning, args.critical),\
        FilesystemUsageSummary(),
        )
        
    check.main(verbose=args.verbose)

if __name__ == '__main__':
    main()
