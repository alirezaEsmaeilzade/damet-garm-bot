import os

class Dbconfig:
    database = os.environ.get('POSTGRES_DB', "testdb")
    user = os.environ.get('POSTGRES_USER', "postgres")
    password = os.environ.get('POSTGRES_PASSWORD', "myPassword")
    host = os.environ.get('POSTGRES_HOST', "127.0.0.1")
    port = os.environ.get('POSTGRES_PORT', "5432")