from EDGAR.Objects.Filing import *
from EDGAR.Objects.Index import *
from datetime import datetime


class Edgar:
    def __init__(self):
        pass

    @staticmethod
    def get_indexes(start_year=1993, quarters=range(1, 4)):
        years = range(start_year, int(datetime.now().year))
        return [Index(year, quarter) for year in years for quarter in quarters]

    @staticmethod
    def get_dates(start=1993, end=datetime.now(), quarters=range(1, 4)):
        for year in range(start, int(end)):
            for quarter in quarters:
                yield (year, quarter)

    @staticmethod
    def fetch_indices_for(dates):
        for year, quarter in dates:
            yield Index(year, quarter)

    @staticmethod
    def fetch_filings_from(indices):
        for index in indices:
            for filing in index.filings:
                yield Filing(filing).json()
