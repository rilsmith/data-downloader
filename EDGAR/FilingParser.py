import json
import pika
import pandas
from EDGAR.Utils.UsGaap import *


class ParseDownload:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=''))
        self.channel = self.connection.channel()
        self.downloaded_queue = self.channel.queue_declare(queue='downloaded')
        self.parsed_queue = self.channel.queue_declare(queue='parsed')

    @staticmethod
    def consume(download_entry):
        data = json.loads(download_entry)
        us_gaap = UsGaap(data['file'])
        data_frame = pandas.DataFrame(data=us_gaap.gaap)
        return data['file'], data_frame

    def publish(self, parsed_file):
        data = {'file': parsed_file}
        self.channel.basic_publish(exchange='', routing_key='parsed', body=json.dumps(data))

    @staticmethod
    def store(parsed_file, data_frame):
        data_frame.to_pickle(re.sub('\..*', '.pkl', parsed_file))

    def process(self, download_entry):
        parsed_file, df = self.consume(download_entry)
        self.store(parsed_file, df)
        self.publish(parsed_file)

    def run(self):
        self.channel.basic_consume(self.process, queue='downloaded', no_ack=True)
        self.channel.start_consuming()
