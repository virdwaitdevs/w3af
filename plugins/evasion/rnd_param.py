'''
rnd_param.py

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

from core.controllers.plugins.evasion_plugin import EvasionPlugin

from core.data.fuzzer.utils import rand_alnum
from core.data.parsers.url import parse_qs
from core.data.url.HTTPRequest import HTTPRequest as HTTPRequest

# options
from core.data.options.opt_factory import opt_factory
from core.data.options.option_list import OptionList


class rnd_param(EvasionPlugin):
    '''
    Add a random parameter.
    @author: Andres Riancho (andres.riancho@gmail.com)
    '''
    def __init__(self):
        EvasionPlugin.__init__(self)

    def modifyRequest(self, request):
        '''
        Mangles the request

        @param request: HTTPRequest instance that is going to be modified by the evasion plugin
        @return: The modified request

        >>> from core.data.parsers.url import URL
        >>> rp = rnd_param()

        >>> u = URL('http://www.w3af.com/')
        >>> r = HTTPRequest( u )
        >>> qs = rp.modifyRequest( r ).url_object.querystring
        >>> len(qs)
        1

        >>> u = URL('http://www.w3af.com/?id=1')
        >>> r = HTTPRequest( u )
        >>> qs = rp.modifyRequest( r ).url_object.querystring
        >>> len(qs)
        2

        >>> u = URL('http://www.w3af.com/?id=1')
        >>> r = HTTPRequest( u, data='a=b' )
        >>> data = parse_qs( rp.modifyRequest( r ).get_data() )
        >>> len(data)
        2

        >>> data = rp.modifyRequest( r ).url_object.querystring
        >>> len(data)
        2

        '''
        # First we mangle the URL
        qs = request.url_object.querystring.copy()
        qs = self._mutate(qs)

        # Finally, we set all the mutants to the request in order to return it
        new_url = request.url_object.copy()
        new_url.querystring = qs

        # Mangle the postdata
        post_data = request.get_data()
        if post_data:

            try:
                # Only mangle the postdata if it is a url encoded string
                post_data = parse_qs(post_data)
            except:
                pass
            else:
                post_data = str(self._mutate(post_data))

        new_req = HTTPRequest(new_url, post_data, request.headers,
                              request.get_origin_req_host())

        return new_req

    def _mutate(self, data):
        '''
        Add a random parameter.

        @param data: A dict-like object.
        @return: The same object with one new key-value.
        '''
        key = rand_alnum()
        value = rand_alnum()
        data[key] = value
        return data

    def get_options(self):
        '''
        @return: A list of option objects for this plugin.
        '''
        ol = OptionList()
        return ol

    def set_options(self, option_list):
        '''
        This method sets all the options that are configured using the user interface
        generated by the framework using the result of get_options().

        @param OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        '''
        pass

    def get_plugin_deps(self):
        '''
        @return: A list with the names of the plugins that should be run before the
        current one.
        '''
        return []

    def getPriority(self):
        '''
        This function is called when sorting evasion plugins.
        Each evasion plugin should implement this.

        @return: An integer specifying the priority. 100 is run first, 0 last.
        '''
        return 50

    def get_long_desc(self):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This evasion plugin adds a random parameter.

        Example:
            Input:      '/bar/foo.asp'
            Output :    '/bar/foo.asp?alsfkj=f09'
        '''
