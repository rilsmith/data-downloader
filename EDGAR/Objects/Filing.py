from EDGAR.Utils.Gaap import *
import subprocess
import re


class Filing:
    def __init__(self, index_info):
        self.index_info = index_info
        self.gaap = self.parse()

    def xml_path(self):
        index_info = self.index_info
        index_path = index_info['filing_path'].replace('.txt', '-index.htm')
        cmd = ['wget', '-P', '/home/rilsmith/downloads/', 'https://www.sec.gov/Archives/%s' % index_path]
        subprocess.call(cmd)

        with open(index_path.split('/')[-1], 'r') as f:
            for line in f:
                if 'XBRL INSTANCE DOCUMENT' in line:
                    pattern = '%s(.*)xml' % index_info['filing_path'].replace('-', '').replace('.txt', '')
                    xml_path = re.search(pattern, next(f)).group(0)
                    return xml_path

    def fetch(self):
        xml_path = self.xml_path()
        cmd = ['wget', 'https://www.sec.gov/Archives/%s' % xml_path]
        subprocess.call(cmd)
        return self.index_info['filing_path']

    def parse(self):
        gaap = Gaap(self.index_info['filing_path'])
        return gaap.info

    def json(self):
        return self.gaap.info
