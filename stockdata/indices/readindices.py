import pandas as pd

class IndicesList():

    def readIndices(self, exchange):
        df = pd.read_excel(self.indices_file, sheet_name=exchange.upper())
        return df
