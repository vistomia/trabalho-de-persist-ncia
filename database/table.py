import polars as pl

class Table:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pl.scan_csv(file_path).collect()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._update()

    def insert(self, values):
        new_row = pl.DataFrame([values], schema=self.df.schema)
        self.df = self.df.extend(new_row)
    
    def insert_column(self, column_name, values):
        new_col = pl.Series(column_name, values)
        self.df = self.df.with_column(new_col)

    def delete_column(self, column_name):
        self.df = self.df.drop(column_name)

    def delete(self, condition):
        self.df = self.df.filter(~condition)

    def select(self, query: str):
        return pl.SQLContext(my_table=self.df).execute(query)
    
    def _update(self):
        self.df.write_csv(self.file_path)

    def __str__(self):
        return self.df.__str__()

with Table("data.csv") as table:
    table.insert({"ado": 4, "ado_duplicated_0": 2, "ado_duplicated_1": 3})
    table.insert({"ado": 5, "ado_duplicated_0": 3, "ado_duplicated_1": 4})
    table.delete_column("ado_duplicated_1")
    print(table.df)
