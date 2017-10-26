import subprocess
import re


class Index:
    def __init__(self, year, quarter):
        self.index = self.fetch(year, quarter)
        self.filings = self.parse(self.index, [])

    @staticmethod
    def fetch(year, quarter):
        url = 'ftp://anonymous:@ftp.sec.gov/edgar/full-index/%s/QTR%s/company.gz' % (year, quarter)
        cmd = ['wget', '--directory-prefix=indexes', url, '-O', '%s-%s-index.gz' % (year, quarter)]
        subprocess.call(cmd)
        return 'indexes/%s-%s-index.gz' % (year, quarter)

    @staticmethod
    def parse(index, filing_list=None):
        with open(index, 'r') as f:
            for line in f.read():
                if '10-Q' in line:
                    columns = re.split('\s', line)
                    filing = {
                        "filing_id": columns[0],
                        "filing_date": columns[3],
                        "filing_path": columns[4]
                    }
                    filing_list.append(filing)
        return filing_list
