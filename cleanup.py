from sqlalchemy import create_engine, inspect

engine = create_engine('sqlite:///site.db')

with engine.connect() as connection:
    inspector = inspect(engine)
    if '_alembic_tmp_po' in inspector.get_table_names():
        connection.execute('DROP TABLE _alembic_tmp_po')
