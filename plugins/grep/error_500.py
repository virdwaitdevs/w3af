'''
error_500.py

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
import core.data.kb.knowledge_base as kb
import core.data.kb.vuln as vuln
import core.data.constants.severity as severity

from core.controllers.plugins.grep_plugin import GrepPlugin
from core.data.db.disk_set import disk_set


class error_500(GrepPlugin):
    '''
    Grep every page for error 500 pages that haven't been identified as bugs by
    other plugins.

    @author: Andres Riancho (andres.riancho@gmail.com)
    '''

    FALSE_POSITIVE_STRINGS = ('<h1>Bad Request (Invalid URL)</h1>',
                              )

    def __init__(self):
        GrepPlugin.__init__(self)

        self._error_500_responses = disk_set()

    def grep(self, request, response):
        '''
        Plugin entry point, identify which requests generated a 500 error.

        @param request: The HTTP request object.
        @param response: The HTTP response object
        @return: None
        '''
        if response.is_text_or_html() \
            and response.getCode() in xrange(400, 600) \
            and response.getCode() not in (404, 403, 401, 405, 400, 501)\
                and not self._is_false_positive(response):
            self._error_500_responses.add((request, response.id))

    def _is_false_positive(self, response):
        '''
        Filters out some false positives like this one:

        This false positive is generated by IIS when I send an URL that's "odd"
        Some examples of URLs that trigger this false positive:
            - http://127.0.0.2/ext.ini.%00.txt
            - http://127.0.0.2/%00/
            - http://127.0.0.2/%0a%0a<script>alert(\Vulnerable\)</script>.jsp

        @return: True if the response is a false positive.
        '''
        for fps in self.FALSE_POSITIVE_STRINGS:
            if fps in response.getBody():
                return True
        return False

    def end(self):
        '''
        This method is called when the plugin wont be used anymore.

        The real job of this plugin is done here, where I will try to see if
        one of the error_500 responses were not identified as a vuln by some
        of my audit plugins
        '''
        all_vulns = kb.kb.getAllVulns()
        all_vulns_tuples = [(v.getURI(), v.get_dc()) for v in all_vulns]

        for request, error_500_response_id in self._error_500_responses:
            if (request.getURI(), request.get_dc()) not in all_vulns_tuples:
                # Found a err 500 that wasnt identified !!!
                v = vuln.vuln()
                v.set_plugin_name(self.get_name())
                v.setURI(request.getURI())
                v.set_id(error_500_response_id)
                v.set_severity(severity.MEDIUM)
                v.set_name('Unhandled error in web application')
                msg = 'An unidentified web application error (HTTP response code 500)'
                msg += ' was found at: "' + v.getURL() + '".'
                msg += ' Enable all plugins and try again, if the vulnerability still is not'
                msg += ' identified, please verify manually and report it to the w3af developers.'
                v.set_desc(msg)
                kb.kb.append(self, 'error_500', v)

        self.print_uniq(kb.kb.get('error_500', 'error_500'), 'VAR')

    def get_long_desc(self):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin greps every page for error 500 pages that have'nt been caught
        by other plugins. By enabling this, you are enabling a "safety net" that
        will catch all interesting HTTP responses which might lead to a bug or
        vulnerability.
        '''
