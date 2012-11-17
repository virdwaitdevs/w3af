'''
FileNameMutant.py

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

from core.data.fuzzer.mutants.urlparts_mutant import URLPartsMutant
from core.data.dc.data_container import DataContainer
from core.data.request.HTTPQsRequest import HTTPQSRequest


class FileNameMutant(URLPartsMutant):
    '''
    This class is a filename mutant.
    '''
    def __init__(self, freq):
        URLPartsMutant.__init__(self, freq)

    def get_mutant_type(self):
        return 'url filename'

    def getURL(self):
        '''
        @return: The URL, as modified by "set_mod_value()"
                '''
        domain_path = self._freq.getURL().getDomainPath()

        # Please note that this double encoding is needed if we want to work
        # with mod_rewrite
        encoded = urllib.quote_plus(self._mutant_dc['modified_part'],
                                    self._safe_encode_chars)
        if self._double_encoding:
            encoded = urllib.quote_plus(encoded, safe=self._safe_encode_chars)

        domain_path.setFileName(self._mutant_dc['start'] + encoded +
                                self._mutant_dc['end'])
        return domain_path

    getURI = getURL

    def getData(self):
        return None

    def print_mod_value(self):
        fmt = 'The sent %s is: "%s%s%s".'
        return fmt % (self.get_mutant_type(), self._mutant_dc['start'],
                      self._mutant_dc['modified_part'], self._mutant_dc['end'])

    def set_mod_value(self, val):
        self._mutant_dc['modified_part'] = val

    def get_mod_value(self):
        return self._mutant_dc['modified_part']

    def setURL(self, u):
        msg = 'You can\'t change the value of the URL in a FileNameMutant'\
              ' instance.'
        raise ValueError(msg)

    def found_at(self):
        '''
        @return: A string representing WHAT was fuzzed.
        '''
        fmt = '"%s", using HTTP method %s. The modified parameter was the URL'\
              ' filename, with value: "%s".'
        return fmt % (self.getURL(), self.get_method(), self.get_mod_value())

    @staticmethod
    def create_mutants(freq, mutant_str_list, fuzzable_param_list,
                       append, fuzzer_config, data_container=None):
        '''
        This is a very important method which is called in order to create
        mutants. Usually called from fuzzer.py module.
        '''
        if not fuzzer_config['fuzz_url_filenames']:
            return []

        if not isinstance(freq, HTTPQSRequest):
            return []

        res = []
        fname = freq.getURL().getFileName()
        fname_chunks = [x for x in re.split(r'([a-zA-Z0-9]+)', fname) if x]

        for idx, fn_chunk in enumerate(fname_chunks):

            for mutant_str in mutant_str_list:

                if re.match('[a-zA-Z0-9]', fn_chunk):
                    divided_fname = DataContainer()
                    divided_fname['start'] = ''.join(fname_chunks[:idx])
                    divided_fname['end'] = ''.join(fname_chunks[idx + 1:])
                    divided_fname['modified_part'] = \
                        (fn_chunk if append else '') + \
                        urllib.quote_plus(mutant_str)

                    freq_copy = freq.copy()
                    freq_copy.setURL(freq.getURL())

                    # Create the mutant
                    m = FileNameMutant(freq_copy)
                    m.set_original_value(fn_chunk)
                    m.set_var('modified_part')
                    m.set_mutant_dc(divided_fname)
                    m.set_mod_value(mutant_str)
                    # Special for filename fuzzing and some configurations
                    # of mod_rewrite
                    m.set_double_encoding(False)
                    res.append(m)

                    # The same but with a different type of encoding! (mod_rewrite)
                    m2 = m.copy()
                    m2.set_safe_encode_chars('/')

                    if m2.getURL() != m.getURL():
                        res.append(m2)
        return res
