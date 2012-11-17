'''
google_spider.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
from urllib2 import URLError

import core.controllers.output_manager as om

from core.data.options.opt_factory import opt_factory
from core.data.options.option_list import OptionList
from core.data.search_engines.google import google as google

from core.controllers.plugins.crawl_plugin import CrawlPlugin
from core.controllers.exceptions import w3afException
from core.controllers.exceptions import w3afRunOnce
from core.controllers.misc.is_private_site import is_private_site
from core.controllers.misc.decorators import runonce


class google_spider(CrawlPlugin):
    '''
    Search google using google API to get new URLs
    @author: Andres Riancho (andres.riancho@gmail.com)
    '''

    def __init__(self):
        CrawlPlugin.__init__(self)

        # User variables
        self._result_limit = 300

    @runonce(exc_class=w3afRunOnce)
    def crawl(self, fuzzable_request):
        '''
        @param fuzzable_request: A fuzzable_request instance that contains
                                    (among other things) the URL to test.
        '''
        google_se = google(self._uri_opener)

        domain = fuzzable_request.getURL().getDomain()
        if is_private_site(domain):
            msg = 'There is no point in searching google for "site:%s".'
            msg += ' Google does\'nt index private pages.'
            raise w3afException(msg % domain)

        try:
            g_results = google_se.getNResults(
                'site:' + domain, self._result_limit)
        except:
            pass
        else:
            self._tm.threadpool.map(self._get_fuzzable_requests,
                                    [r.URL for r in g_results])

    def _get_fuzzable_requests(self, url):
        '''
        Generate the fuzzable requests based on the URL, which is a result from
        google search.

        @param url: A URL from google.
        '''
        try:
            response = self._uri_opener.GET(url, cache=True)
        except w3afException, w3:
            msg = 'w3afException while fetching page in google_spider: "%s".'
            om.out.debug(msg % w3)
        except URLError, ue:
            msg = 'URLError while fetching page in google_spider, error: "%s".'
            om.out.debug(msg % ue)
        else:
            for fr in self._create_fuzzable_requests(response):
                self.output_queue.put(fr)

    def get_options(self):
        '''
        @return: A list of option objects for this plugin.
        '''
        ol = OptionList()

        d = 'Fetch the first "result_limit" results from the Google search'
        o = opt_factory('result_limit', self._result_limit, d, 'integer')
        ol.add(o)

        return ol

    def set_options(self, options_list):
        '''
        This method sets all the options that are configured using the user
        interface generated by the framework using the result of get_options().

        @param OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        '''
        self._result_limit = options_list['result_limit'].get_value()

    def get_long_desc(self):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin finds new URL's using google. It will search for
        "site:domain.com" and do GET requests all the URL's found in the result.

        One configurable parameter exists:
            - result_limit
        '''
