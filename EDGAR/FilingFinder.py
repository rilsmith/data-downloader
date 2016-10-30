import os
import re
import json
import pika
import datetime
import subprocess


class FilingFinder:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=''))
        self.channel = self.connection.channel()
        self.download_queue = self.channel.queue_declare(queue='download_queue')

    @staticmethod
    def get_index_for(year, quarter):
        os.mkdir('indexes') if not os.path.exists('indexes') else print('Index Directory Already Exists')
        url = 'ftp://anonymous:@ftp.sec.gov/edgar/full-index/%s/QTR%s/company.gz' % (year, quarter)
        cmd = ['wget', '--directory-prefix=indexes', url, '-O', '%s-%s-index.gz' % (year, quarter)]
        subprocess.call(cmd)
        return 'indexes/%s-%s-index.gz' % (year, quarter)

    def parse(self, index_file, data):
        with open(index_file, 'r') as f:
            for line in f.read():
                if '10-Q' in line:
                    columns = re.split('\s', line)
                    data[columns[0]] = {}
                    data[columns[0]]['filing_date'] = columns[3]
                    data[columns[0]]['filing_path'] = columns[4]
                    self.publish(data)
        return data

    def get_indexes(self, start_year=1993, quarters=range(1, 4)):
        years = range(start_year, int(datetime.datetime.now().year))
        return [self.get_index_for(year, quarter) for year in years for quarter in quarters]

    def publish(self, data):
        self.channel.basic_publish(exchange='', routing_key='download_queue', body=json.dumps(data))

    def run(self):
        indexes = self.get_indexes()
        parsed = [self.parse(index, {}) for index in indexes]
        print(parsed)

if __name__ == '__main__':
    finder = FilingFinder()
    finder.run()
