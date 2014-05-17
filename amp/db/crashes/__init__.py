from amp.db.settings import options
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column
from sqlalchemy import BigInteger, Integer, DateTime, TEXT as String

engine = create_engine(options.crashesdb, pool_recycle=14400)
metadata = MetaData()
metadata.bind = engine
crashes = Table('crashes', metadata,
                Column('id', BigInteger, primary_key=True, autoincrement=True),
                Column('crash', String, unique=True),
                Column('crashtime', DateTime, index=True),
                Column('version', String),
                Column('version_code', Integer),
                Column('crash_line', String),
                Column('extras', String),
                Column('uploadtime', DateTime, index=True),
                Column('crashed_thread_stacktrace', String),
                Column('crash_reason', String),
                Column('crash_address', String))


from sqlalchemy.engine.reflection import Inspector

def get_apps():
    inspector = Inspector.from_engine(engine)
    schemas = set(inspector.get_schema_names())
    schemas.discard('information_schema')
    return schemas
