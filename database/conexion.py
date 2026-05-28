import pymysql
import os
from dotenv import load_dotenv


load_dotenv()

def conectar_db():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT")),
        connect_timeout=10,
        autocommit=True
    )