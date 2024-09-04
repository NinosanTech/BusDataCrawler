from DataCrawler.serializer import Serializer
from datetime import datetime
from pandas import concat
from pandas import DataFrame as df

if __name__ == '__main__':
    serializer = Serializer()
    with Serializer() as serializer:
        tables = serializer.read("SELECT * FROM information_schema.tables")
        data = df()
        for table in tables.itertuples():
            try:
                table_parsed = datetime.strptime(table.TABLE_NAME,"%d/%m/%Y")
                data = concat([data, serializer.read(f"SELECT * FROM [{table.TABLE_SCHEMA}].[{table.TABLE_NAME}]")])
            except ValueError:
                pass
        print(valid_table_names)
