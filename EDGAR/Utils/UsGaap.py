import re


class UsGaap:
    def __init__(self, filing):
        self.filing = filing
        self.gaap = self.parse(self.filing)

    @staticmethod
    def get_context_date(filing):
        date = filing.split('-').split('.')[0]
        day = date[-2:]
        year = date[:4]
        month = date[4:6]
        return day, month, year

    def parse(self, filing):
        gaap_info = {}
        with open(filing, 'r') as f:
            for line in f.read():
                day, month, year = self.get_context_date(filing)
                if re.search('^<us-gaap:.*Context_As_Of_%s_%s_%s' % (day, month, year), line):
                    #   TODO: Add code to parse context for current line item
                    match = re.search('^<us-gaap:([a-zA-Z]*)\s.*>(.*)</us-gaap.*>', line)
                    gaap_info[match.group(1)] = match.group(2)
            return gaap_info

    def get_cash(self):
        return self.gaap['Cash'] if 'Cash' in self.gaap.keys() else 0

    def get_assets(self):
        return self.gaap['Assets'] if 'Assets' in self.gaap.keys() else 0

    def get_liabilities(self):
        return self.gaap['Liabilities'] if 'Liabilities' in self.gaap.keys() else 0

    def get_equity(self):
        return self.gaap['StockholdersEquity'] if 'StockholdersEquity' in self.gaap.keys() else 0

    def get_shares(self):
        return self.gaap['CommonStockSharesOutstanding'] if 'CommonStockSharesOutstanding' in self.gaap.keys() else 0

    def get_net_income(self):
        return self.gaap['NetIncomeLoss'] if 'NetIncomeLoss' in self.gaap.keys() else 0

    def get_receivables(self):
        receivables = ['NotesReceivableNet', 'AccountsReceivableNet']
        return sum([self.gaap[r] for r in receivables if r in self.gaap.keys() and self.gaap[r] is not None])

    def get_current_assets(self):
        return self.get_cash() + self.get_receivables()

    def get_current_liabilities(self):
        return self.gaap['AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent'] \
            if 'AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent' in self.gaap.keys() else 0

    def get_earnings_per_share(self):
        #   Get from filing OR
        #   (Net income - dividends) / oustanding shares
        pass

    #   TODO: Consider creating new class for calculations
    def get_book_value(self):
        return self.get_assets() - self.get_liabilities()

    def current_ratio(self):
        #   Value investing >= 1.5
        return self.get_current_assets() / self.get_current_liabilities()

    def return_on_equity(self):
        #   Value investing >= .08
        return self.get_net_income() / self.get_equity()

    def debt_equity_ratio(self):
        #   Value investing <= .5
        return self.get_liabilities() / self.get_equity()

    def stock_stability(self):
        #   Stable if correlates to EPS growth
        return self.get_equity() / self.get_shares()

    def price_to_earnings(self, price):
        #   <= 15?
        return price / self.get_earnings_per_share()

    def price_to_book(self, price):
        return (price / self.get_shares()) / (self.get_book_value() / self.get_shares())
