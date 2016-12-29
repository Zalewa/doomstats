from django.db import connection
from doomstats import settings
from time import time
from operator import add
import re


# http://stackoverflow.com/a/17777539
class StatsMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        In your base template, put this:
        <p>
        <!-- DEBUG STATS: Total: %(total_time).2fs Python: %(python_time).2fs DB: %(db_time).2fs Queries: %(db_queries)d ENDSTATS -->
        <!-- RELEASE STATS: Page prepared in: %(total_time).2fs. ENDSTATS -->
        </p>
        '''

        # get number of db queries before we do anything
        n = len(connection.queries)

        # time the view
        start = time()
        response = view_func(request, *view_args, **view_kwargs)
        total_time = time() - start

        # compute the db time for the queries just run
        db_queries = len(connection.queries) - n
        if db_queries:
            db_time = reduce(add, [float(q['time'])
                                   for q in connection.queries[n:]])
        else:
            db_time = 0.0

        # and backout python time
        python_time = total_time - db_time

        stats = {
            'total_time': total_time,
            'python_time': python_time,
            'db_time': db_time,
            'db_queries': db_queries,
        }

        # replace the comment if found
        if response and response.content:
            s = response.content
            regexp = self.__template_matcher()
            match = regexp.search(s)
            if match:
                s = (s[:match.start('cmt')] +
                     match.group('fmt') % stats +
                     s[match.end('cmt'):])
                response.content = s

        return response

    def __template_matcher(self):
        if settings.DEBUG:
            return re.compile(r'(?P<cmt><!--\s*DEBUG STATS:(?P<fmt>.*?)ENDSTATS\s*-->)')
        else:
            return re.compile(r'(?P<cmt><!--\s*RELEASE STATS:(?P<fmt>.*?)ENDSTATS\s*-->)')
