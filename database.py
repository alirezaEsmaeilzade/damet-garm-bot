import psycopg2
from psycopg2.extensions import AsIs
from config import Dbconfig


class DB:
    @staticmethod
    def makeTable():
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
                      UserID            INT     NOT NULL,
                      PinCapacity            INT     DEFAULT 5);''')
        cur.execute('''CREATE TABLE IF NOT EXISTS storeUsersPin(
                          Name         VARCHAR(255)    NOT NULL,
                          One            INT     DEFAULT 0,
                          Two            INT     DEFAULT 0,
                          Three            INT     DEFAULT 0,
                          Four            INT     DEFAULT 0,
                          Five            INT     DEFAULT 0);''')
        con.commit()
        con.close()

    @staticmethod
    def GetInfoForSendReportInGroup():
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute("select exists(select 1 from storeUsersPin);")
        x = cur.fetchone()
        if x[0] == False:
            con.commit()
            con.close()
            return None
        cur.execute("select * from storeUsersPin;")
        x = cur.fetchall()
        con.commit()
        con.close()
        return x

    @staticmethod
    def storeUserDataInDB(inputData, column, userID):
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute('''UPDATE users
                    SET %s=%s
                    WHERE UserID=%s''', (AsIs(column), inputData, userID))
        con.commit()
        con.close()

    @staticmethod
    def isUserExist(userID):
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute("select exists(select 1 from users where UserID=%s);", (userID,))
        x = cur.fetchone()
        con.commit()
        con.close()
        return x[0]

    @staticmethod
    def insertUser(userID):
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute("""INSERT INTO users (UserID)
                        VALUES (%s);""", (userID,))
        con.commit()
        con.close()

    @staticmethod
    def getPinCapacity(userID):
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute('SELECT PinCapacity FROM users WHERE UserID=%s ', (userID,))
        x = cur.fetchone()
        con.commit()
        con.close()
        return int(x[0])

    @staticmethod
    def storeDataOfReceiverInDB(pin, name, inputType):
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute("select exists(select 1 from storeUsersPin where Name=%s);", (name,))
        x = cur.fetchone()
        if x[0] == False:
            cur.execute("""INSERT INTO storeUsersPin (Name)
                VALUES (%s);""", (name,))
        cur.execute('SELECT %s FROM storeUsersPin WHERE Name=%s ', (AsIs(inputType), name,))
        x = cur.fetchone()
        cur.execute('''UPDATE storeUsersPin
            SET %s=%s
            WHERE Name=%s''', (AsIs(inputType), x[0] + pin, name,))
        con.commit()
        con.close()

    @staticmethod
    def resetAllPinCapacityOfReceiver():
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute("UPDATE users SET pincapacity=5;")
        con.commit()
        con.close()

    @staticmethod
    def deletetDataOfReceiver():
        con = psycopg2.connect(database=Dbconfig.database, user=Dbconfig.user,
                               password=Dbconfig.password, host=Dbconfig.host, port=Dbconfig.port)
        cur = con.cursor()
        cur.execute("DELETE FROM storeUsersPin;")
        con.commit()
        con.close()
