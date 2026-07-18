from connections import engine
from sqlalchemy import inspect
inspector = inspect(engine)
table_names = inspector.get_table_names()   
for table in table_names:
    columns = inspector.get_columns(table)
    foreign_keys = inspector.get_foreign_keys(table)



def get_schema_description():
    description = ""
    for table in table_names:
        columns = inspector.get_columns(table)
        column_strs = [f"{col['name']} ({str(col['type'])})" for col in columns]
        description += f"Table: {table}\nColumns: {', '.join(column_strs)}\n"

        foreign_keys = inspector.get_foreign_keys(table)
        if foreign_keys:
            fk_strs = [f"{fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}" for fk in foreign_keys]
            description += f"Foreign Keys: {', '.join(fk_strs)}\n"

        description += "\n"
    return description
print(get_schema_description())

