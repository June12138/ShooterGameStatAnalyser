import pandas as pd

class MyDF(pd.DataFrame):
    idField = "ID"
    def getRowByID(self, id):
        return self[self[self.idField] == id]
    def QuickSearch(self, searchField, searchKey, returnKey):
        return self[self[searchField] == searchKey].iloc[0][returnKey]
    def SearchContain(self, searchField, searchKey, returnKey):
        for i in range(0,len(self)):
            currentRow = self.iloc[i]
            if (searchKey in str(currentRow[searchField])):
                return currentRow[returnKey]
class ExTable(MyDF):
    def __init__(self, path, sheetName, skipRows = [], idField = "ID"):
        super().__init__(pd.read_excel(path, sheet_name = sheetName, skiprows=skipRows))
        self.idField = idField

class CSVTable(MyDF):
    def __init__(self, path, skipRows = [], idField = "---"):
        super().__init__(pd.read_csv(path, skiprows=skipRows))
        self.idField = idField

def QuickSearch(table, searchField, searchKey, returnKey):
    return table[table[searchField] == searchKey].iloc[0][returnKey]
def SearchContain(table, searchField, searchKey, returnKey):
    for i in range(0,len(table)):
        currentRow = table.iloc[i]
        if (searchKey in str(currentRow[searchField])):
            return currentRow[returnKey]