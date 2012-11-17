'''
bing.py

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
import urllib
import re

from core.data.search_engines.search_engine import SearchEngine
from core.data.parsers.url import URL


class bing(SearchEngine):
    '''
    This class is a wrapper for doing bing searches. It allows the user to use
    GET requests to search bing.com.

    @author: Andres Riancho (andres.riancho@gmail.com)
    '''
    BLACKLISTED_DOMAINS = set(['cc.bingj.com', 'www.microsofttranslator.com',
                               'onlinehelp.microsoft.com', 'go.microsoft.com'])

    def __init__(self, urlOpener):
        SearchEngine.__init__(self)
        self._uri_opener = urlOpener

    def search(self, query, start, count=10):
        '''
        Search the web with Bing.

        This method is based from the msn.py file from the massive enumeration toolset,
        coded by pdp and released under GPL v2.
        '''
        class BingResult:
            '''
            Dummy class that represents the search result.
            '''
            def __init__(self, url):
                if not isinstance(url, URL):
                    msg = 'The url __init__ parameter of a BingResult object must'
                    msg += ' be of url.URL type.'
                    raise ValueError(msg)

                self.URL = url

            def __repr__(self):
                return '<bing result %s>' % self.URL

        url = 'http://www.bing.com/search?'
        query = urllib.urlencode(
            {'q': query, 'first': start + 1, 'FORM': 'PERE'})
        url_instance = URL(url + query)
        response = self._uri_opener.GET(url_instance, headers=self._headers,
                                        cache=True, grep=False)

        # This regex might become outdated, but the good thing is that we have
        # test_bing.py which is going to fail and tell us that it's outdated
        re_match = re.findall('<a href="((http|https)(.*?))" h="ID=SERP,',
                              response.getBody())

        results = []

        for url, _, _ in re_match:
            try:
                url = URL(url)
            except:
                pass
            else:
                if url.getDomain() not in self.BLACKLISTED_DOMAINS:
                    results.append(BingResult(url))

        return results
