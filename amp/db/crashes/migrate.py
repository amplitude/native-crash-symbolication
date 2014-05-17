from sqlalchemy import MetaData, Table, Column, BigInteger, TEXT, DateTime, Integer

from amp.db.crashes import get_apps, engine


def v1(schema):
    print '%s - 1' % (schema,)
    metadata = MetaData(schema=schema)
    Table('crashes', metadata,
          Column('id', BigInteger, primary_key=True, autoincrement=True),
          Column('crash', TEXT, unique=True),
          Column('crashtime', DateTime, index=True),
          Column('version', TEXT),
          Column('version_code', Integer),
          Column('crash_line', TEXT)).create(engine, checkfirst=True)

def v2(schema):
    print '%s - 2' % (schema,)
    conn = engine.connect()
    conn.execute("ALTER TABLE {schema}.crashes ADD COLUMN extras TEXT".format(schema=schema))
    conn.close()

def upgrade(schema):
    v1(schema)
    v2(schema)

if __name__ == '__main__':
    for app in get_apps():
        upgrade(app)
