import mysql.connector as sqlcon
from mysql.connector import Error, errorcode
import os
import dotenv

dotenv.load_dotenv()


def connect_to_db():
    try:
        cnx = sqlcon.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            port=os.environ['DB_PORT']
        )
        if cnx.is_connected():
            db_info = cnx.get_server_info()
            print("Connected to MySQL Server version ", db_info)
            cursor = cnx.cursor()
            cursor.execute("SHOW DATABASES;")
            if not (os.environ['DB_NAME'],) in cursor.fetchall():
                print("Database does not exist")
                cursor.execute("CREATE DATABASE " + os.environ['DB_NAME'])
                print("Database created successfully")
            cursor.execute(f"USE {os.environ['DB_NAME']};")
            print("Connected to %s Database" % os.environ['DB_NAME'])
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if not ("users",) in tables or not ("time_record",) in tables:
                cursor.execute("CREATE TABLE IF NOT EXISTS users "
                               "(id INT PRIMARY KEY AUTO_INCREMENT, "
                               "username VARCHAR(255) NOT NULL,"
                               "teleId VARCHAR(255) NOT NULL, "
                               "INDEX idx_teleId (teleId),"
                               "isAdmin BOOLEAN DEFAULT FALSE);")
                cursor.execute("CREATE TABLE IF NOT EXISTS time_record"
                               "(id INT PRIMARY KEY AUTO_INCREMENT,"
                               "teleId VARCHAR(255) NOT NULL,"
                               "date_now DATE NOT NULL,"
                               "check_in TIME,"
                               "break_out1 TIME,"
                               "break_in1 TIME,"
                               "break_out2 TIME,"
                               "break_in2 TIME,"
                               "check_out TIME);")
                print("Table created successfully")
            cursor.close()
            return cnx
    except Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
            return False
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
            return False
        else:
            print("Something is wrong : ", e)
            return False


def show_all_columns_name(cnx, table_name, db_name):
    cursor = cnx.cursor()
    sql = ("SELECT COLUMN_NAME"
           " FROM INFORMATION_SCHEMA.COLUMNS"
           " WHERE table_name = %s"
           " AND table_schema = %s")
    vals = (str(table_name), str(db_name))
    cursor.execute(sql, vals)
    result = cursor.fetchall()
    cursor.close()
    return result


def regist_member(cnx, username, tele_id, is_admin):
    cursor = cnx.cursor()
    sql = "INSERT INTO users (username, teleId, isAdmin) VALUES (%s, %s, %s)"
    vals = (username, str(tele_id), is_admin)
    cursor.execute(sql, vals)
    cnx.commit()
    cursor.close()


def check_member_exists(cnx, tele_id):
    cursor = cnx.cursor()
    sql = "SELECT * FROM users WHERE teleId = %s"
    cursor.execute(sql, (str(tele_id),))
    is_registered = cursor.fetchone()
    cursor.close()
    return True if is_registered else False


def insert_record_time(cnx, tele_id, date_now):
    cursor = cnx.cursor()
    sql = "INSERT INTO time_record (teleId, date_now) VALUES (%s, %s)"
    vals = (str(tele_id), date_now)
    cursor.execute(sql, vals)
    cnx.commit()
    cursor.close()


def today_record_was_created(cnx, tele_id, today_date):
    cursor = cnx.cursor()
    sql = "SELECT * FROM time_record WHERE teleId = %s AND date_now = %s"
    vals = (str(tele_id), today_date)
    cursor.execute(sql, vals)
    exists = cursor.fetchone()
    cursor.close()
    return True if exists else False


def update_record_time(cnx, tele_id, date_now, **kwargs):
    cursor = cnx.cursor()
    columns = show_all_columns_name(
        cnx,
        'time_record',
        os.environ['DB_NAME']
    )
    for k in kwargs:
        if (k,) in columns:
            sql = (f"UPDATE time_record SET {k} = %s"
                   " WHERE teleId = %s AND date_now = %s")
            vals = (kwargs[k], str(tele_id), date_now)
            cursor.execute(sql, vals)
    cursor.close()
    cnx.commit()


def check_record_set(cnx, tele_id, date_now, col_name):
    cursor = cnx.cursor()
    columns = show_all_columns_name(
        cnx,
        'time_record',
        os.environ['DB_NAME']
    )
    if (col_name,) in columns:
        sql = (f"SELECT {col_name} FROM time_record WHERE teleId = %s"
               f" AND date_now = %s")
        vals = (str(tele_id), date_now)
        cursor.execute(sql, vals)
        record = cursor.fetchone()
        cursor.close()
        return record
    else:
        return False
