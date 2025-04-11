import pandas as pd

class MyTable(pd.DataFrame):
    def __init__(self, path, sheetName, skipRows = [], idField = "ID"):
        super().__init__(pd.read_excel(path, sheet_name = sheetName, skiprows=skipRows))
        self.idField = idField
    def getRowByID(self, id):
        return self[self[self.idField] == id]