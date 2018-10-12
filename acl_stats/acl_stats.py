#!/usr/bin/env python
# -*- coding: utf-8 -*
"""Python script to consolidade ACL stats"""

import sys
import time
import datetime
import io
import json
import csv
import requests
from colorama import Fore, Back, Style, init
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

init(autoreset=True)
"""
Results:
    {   '0x11as1':
            {
            'line'      : 1,
            'hitcount'  : 10,
            'timestamp' : 4123121,
            'entry'     : 'access-list inside_access_in line 48 extended permit tcp 172.16.0.0 255.240.0.0 172.26.254.0 255.255.254.0 eq www (hitcnt=115315) 0xac84dc7d'
            }
    }
"""

class RespFetcherHttps:
    """Response fetcher."""

    def __init__(
        self, 
        username='cisco',
        password='cisco',
        base_url='https://172.21.128.227/admin/config',
        timeout=30
    ):
        """Class init."""
        self.username = username
        self.password = password
        self.base_url = base_url
        self.timeout = timeout
        self.token = ""
        self.session = requests.Session()
        self.headers = {'Content-Type': 'text/xml'}

    def test_connection(self):
        """ Test connection to ASA via the ASDM Interface"""
        response = self.get_resp(endpoint="/show+version", returnObject=True)

        if response.status_code is 200:
            return (True, 200)
        else:
            return (False, response.status_code)

        return response

    def get_resp(self, endpoint="", data=None, params={}, throw=True, returnObject=False):
        """Get response from device and returne parsed json."""
        full_url = self.base_url + endpoint
        f = None
        try:
            if data is not None:
                f = self.session.post(full_url, data=data, auth=(self.username, self.password),
                                      headers=self.headers, timeout=self.timeout,
                                      params=params, verify=False)
            else:
                f = self.session.get(full_url, auth=(self.username, self.password),
                                     headers=self.headers, timeout=self.timeout,
                                     params=params, verify=False)
            if (f.status_code != 200):
                if throw:
                    errMsg = "Operation returned an error: {}".format(f.status_code)
                    raise Exception(errMsg)
                else:
                    return False

            if returnObject:
                return f
            else:
                return f.text
        except requests.exceptions.RequestException as e:
            if throw:
                raise Exception(e)
            else:
                return False


class ACLStats(object):

    def __init__(self,
                 hostname=None,
                 username=None,
                 password=None,
                 port=443,
                 acl_name=None,
                 acl_file=None,
                 acl_brief=None,
                 timeout=60,
                 output="csv",
                 write_to=None):
        """Class init"""

        self.hostname = hostname
        self.username = username
        self.password = password
        self.acl_name = acl_name
        self.acl_file = acl_file
        self.acl_brief = acl_brief
        self.output = output
        self.output_file = write_to
        self.port = port
        self.results = {}
        self.briefs = {}
        self.lines_processed = 0
        self.matches = 0
        self.start_time = time.time()


    def generate_csv(self, r=None):
        output = io.StringIO()
        fieldnames = ['entry_id', 'grouped_id', 'line', 'hitcount', 'last_hit_date', 'timestamp', 'entry']
        wr = csv.DictWriter(output, fieldnames)
        wr.writeheader()
        wr.writerows(r.values())

        return output.getvalue()

    def output_results(self, r=None):
        results = None
        if self.output == 'csv':
            results = self.generate_csv(r)
        elif self.output == 'json':
            results = json.dumps(list(r.values()), indent=2)

        if self.output_file is not None:
            print(Fore.YELLOW + Style.BRIGHT + "Writing file")
            ofile = open(self.output_file, 'w')
            ofile.write(results)
            ofile.close()
            print(Fore.GREEN + Style.BRIGHT + "Done!")
        else:
            print(Fore.GREEN + Style.BRIGHT + "Done!")
            print(results)
    
    def process_acl(self, acl="", is_file=False):
        parsed_acl = ""
        if is_file is True:
            parsed_acl = acl
        else:
            parsed_acl = acl.splitlines()

        for line in parsed_acl:
            if 'name hash' in line or 'remark' in line:
                continue
            line_parts = line.strip().split()
            clean_id = line_parts[-1][2:]
            self.results[clean_id] = {'entry_id': clean_id, 'grouped_id': '-', 'line': line_parts[3], 'hitcount': 0, 'last_hit_date': "0", 'timestamp': 0, 'entry': line.strip() }
            self.lines_processed += 1

    def process_acl_brief(self, acl_brief="", is_file=False):
        parsed_acl_brief = ""
        if is_file is True:
            parsed_acl_brief = acl_brief
        else:
            parsed_acl_brief = acl_brief.splitlines()

        for line in parsed_acl_brief:
            if 'name hash' in line or 'remark' in line:
                continue
            line_parts = line.split()
            acl_id = line_parts[0]
            #briefs[acl_id] = {}
            if acl_id in self.results.keys():
                self.results[acl_id]['grouped_id'] = '{}'.format(line_parts[1])
                self.results[acl_id]['hitcount'] = int(line_parts[2], 16)
                self.results[acl_id]['last_hit_date'] = datetime.datetime.fromtimestamp(int(line_parts[-1], 16)).strftime('%Y-%m-%d %H:%M:%S')
                self.results[acl_id]['timestamp'] = int(line_parts[-1], 16)
                self.matches += 1
                self.lines_processed += 1

    def process_files(self):
        print(Fore.YELLOW + Style.BRIGHT + 'Opening ACL File')
        acl_file = open(self.acl_file, 'r')
        print(Fore.YELLOW + Style.BRIGHT + 'Opening ACL Brief File')
        brief_file = open(self.acl_brief, 'r')
        print(Fore.YELLOW + Style.BRIGHT + "Processing")
        self.process_acl(acl=acl_file, is_file=True)

        self.process_acl_brief(acl_brief=brief_file, is_file=True)

        self.output_results(self.results)

        acl_file.close()
        brief_file.close()

        self.print_final_stats()


    def process_live(self):
        print(Fore.BLUE + Style.BRIGHT + '\nContacting Device')
        base_url = "https://{}:{}/admin/exec".format(self.hostname, self.port)
        fetcher = RespFetcherHttps(username=self.username, password=self.password, base_url=base_url)
        acl_endpoint = "/show+access-list+{}".format(self.acl_name)
        print(Fore.YELLOW + Style.BRIGHT + 'Fetching ACL')
        acl = fetcher.get_resp(endpoint=acl_endpoint)
        acl_brief_endpoint = "/show+access-list+{}+brief".format(self.acl_name)
        print(Fore.YELLOW + Style.BRIGHT + 'Fetching ACL Brief')
        acl_brief = fetcher.get_resp(endpoint=acl_brief_endpoint)
        print(Fore.YELLOW + Style.BRIGHT + "Processing")
        self.process_acl(acl=acl)
        self.process_acl_brief(acl_brief=acl_brief)

        self.output_results(self.results)

        self.print_final_stats()


    def print_final_stats(self):
        print(Fore.CYAN + "Lines processed (acls + brief): {}".format(self.lines_processed))
        print(Fore.CYAN + "Total execution time: {}s. \n".format((time.time() - self.start_time)))
