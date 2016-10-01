import re
import json
import pika
import subprocess


class FilingFetcher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='')
        self.download_queue = self.channel.queue_declare(queue='download_queue')
        self.downloaded = self.channel.queue_declare(queue='downloaded')

    def xml_path(self, filing):
        index_path = filing.replace('.txt', '-index.htm')
        cmd = ['wget', '-P', '/home/rilsmith/downloads/', 'https://www.sec.gov/Archives/%s' % index_path]
        subprocess.call(cmd)

        with open(index_path.split('/')[-1], 'r') as f:
            for line in f:
                if re.search('XBRL INSTANCE DOCUMENT', line):
                    pattern = '%s(.*)xml' % filing.replace('-', '').replace('.txt', '')
                    xml_path = re.search(pattern, next(f)).group(0)
                    return xml_path

    def consume(self, catalog_entry):
        data = json.loads(catalog_entry)
        xml_path = self.xml_path(data['filing_path'])
        cmd = ['wget', 'https://www.sec.gov/Archives/%s' % xml_path]
        subprocess.call(cmd)
        return data['filing_path']

    def publish(self, downloaded_file):
        data = {'file': downloaded_file}
        self.channel.basic_publish(exchange='', routing_key='downloaded', body=json.dumps(data))

    def process(self, catalog_entry):
        downloaded_file = self.consume(catalog_entry)
        self.publish(downloaded_file)

    def run(self):
        self.channel.basic_consume(self.process, queue='download_queue', no_ack=True)
        self.channel.start_consuming()

if __name__ == '__main__':
    filing_fetcher = FilingFetcher()
    filing_fetcher.run()
