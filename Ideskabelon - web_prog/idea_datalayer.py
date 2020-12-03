from flask import g
import sqlite3

class IdeaData():

    def __init__(self):
        self.DATABASE = 'ideahouse.db'

        self._create_db_tables()
        c = self._get_db().cursor()

        c.execute("SELECT * FROM UserProfiles;")
        for u in c:
            print(u)


    def _get_db(self):
        db = g.get('_database', None)
        if db is None:
            db = g._databdase = sqlite3.connect(self.DATABASE)
        return db

    def close_connection(self):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    def get_number_of_ideas(self):
        c = self._get_db().cursor()
        c.execute("SELECT COUNT(rowid) FROM Ideas;")
        val = c.fetchone()
        if val is not None:
            return val[0]
        else:
            return None

    def get_idea_list(self, userid, ideaid = None):
        db = self._get_db()
        c = db.cursor()
        if ideaid is not None:
            c.execute("SELECT idea FROM Ideas WHERE id = ?", ideaid)
            t = c.fetchone()
            print("Idéen er: {}".format(t[0]))
            c.execute("""SELECT Ideas.id, idea, timestamp, UserProfiles.username FROM Ideas JOIN UserProfiles ON Ideas.userid = UserProfiles.id WHERE idea LIKE ?""", (t[0],))
        else:
            c.execute("""SELECT Ideas.id, idea, timestamp, UserProfiles.username FROM Ideas JOIN UserProfiles ON Ideas.userid = UserProfiles.id WHERE userid = ?""",(userid,))
        idea_list = []
        for i in c:
            idea_list.append({'id':i[0], 'text':i[1], 'date':i[2], 'user': i[3]})
        return idea_list


    def register_new_idea(self, idea, id):
        db = self._get_db()
        c = db.cursor()
        c.execute("""INSERT INTO Ideas (idea, userid) VALUES (?, ?);""",(idea, id))
        db.commit()

    def get_idea_count(self, userid):
        c = self._get_db().cursor()
        c.execute("SELECT count(rowid) FROM Ideas WHERE userid == ?;", (userid,))
        n = c.fetchone()
        return n[0]

    def get_user_id(self, s):
        c = self._get_db().cursor()
        c.execute("SELECT id FROM UserProfiles WHERE username = ?", (s,))
        r = c.fetchone()
        #If the user doesn't exist, the result will be None
        if r is not None:
            return r[0]
        else:
            return None

    def register_user(self, user, pw, email):
        db = self._get_db()
        c = db.cursor()
        c.execute("SELECT * from UserProfiles WHERE username = ? OR email = ?", (user,email))
        r = c.fetchone()
        res = False
        if r is not None:
            #The username og email is already in use
            res = False
        else:
            c.execute("INSERT INTO UserProfiles (username, password, email) VALUES (?,?,?)", (user,pw,email))
            db.commit()
            res = True
        return res

    def get_user_list(self):
        l = []
        c = self._get_db().cursor()
        c.execute('SELECT * FROM UserProfiles;')
        for u in c:
            l.append("Navn: {}, email: {}, pw: {}".format(u[1],u[2],u[3]))
        return l

    def login_success(self, user, pw):
        c = self._get_db().cursor()
        c.execute("SELECT password FROM UserProfiles WHERE username = ?", (user,))
        r = c.fetchone()
        if r is not None:
            db_pw = r[0]
        else:
            return False
        return db_pw == pw

#Table Vars
    def register_vars(self, userid, navn, type, view):
        db = self._get_db()
        c = db.cursor()
        c.execute("INSERT INTO Vars (userid, navn, type, view) VALUES (?,?,?,?)", (userid,navn,type,view))
        db.commit()

    def get_tracker_list(self, userid, trackerid = None):
        db = self._get_db()
        c = db.cursor()
        if trackerid is not None:
            c.execute("SELECT navn FROM Vars WHERE id = ?", trackerid)
            t = c.fetchone()
            print("Trackeren er: {}".format(t[0]))
            c.execute("""SELECT Vars.id, navn, UserProfiles.username FROM Vars JOIN UserProfiles ON Vars.userid = UserProfiles.id WHERE navn LIKE ?""", (t[0],))
            #c.execute("""SELECT Ideas.id, idea, timestamp, UserProfiles.username FROM Ideas JOIN UserProfiles ON Ideas.userid = UserProfiles.id WHERE idea LIKE ?""", (t[0],))
        else:
            c.execute("""SELECT Vars.id, navn, UserProfiles.username FROM Vars JOIN UserProfiles ON Vars.userid = UserProfiles.id WHERE userid = ?""",(userid,))
            # c.execute("""SELECT Ideas.id, idea, timestamp, UserProfiles.username FROM Ideas JOIN UserProfiles ON Ideas.userid = UserProfiles.id WHERE userid = ?""",(userid,))
        tracker_list = []
        for i in c:
            tracker_list.append({'id':i[0], 'navn':i[1], 'user': i[2]})
        print(tracker_list)
        return tracker_list

    def add_track_data(self, input, id):
        db = self._get_db()
        c = db.cursor()
        c.execute("INSERT INTO Observation (value, varid) VALUES (?,?)", (input,id))
        db.commit()

    def get_graf_list(self, varid):
        db = self._get_db()
        c = db.cursor()
        print("varid: {}".format(varid))
        #c.execute("SELECT value FROM Observation WHERE varid = ?", varid)
        #c.execute("""SELECT value, timestamp FROM Observation""", [varid])
        c.execute("SELECT value, timestamp FROM Observation""")
        print(c)
        graf_list = []
        for i in c:
            graf_list.append({'value':i[0], 'timestamp':i[1]})
        print("graf_list: {}".format(graf_list))
        return graf_list


#Tabel Observation


    def _create_db_tables(self):
        db = self._get_db()
        #try:
        #    db.execute("DROP TABLE IF EXISTS Ideas;")
        #    db.commit()
        #except:
        #    print('Fejl ved sletning af tabeller.')
        c = db.cursor()
        try:
            c.execute("""CREATE TABLE UserProfiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT,
                password TEXT);""")
        except Exception as e:
            print(e)

        try:
            c.execute("""CREATE TABLE Ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER,
                idea TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);""")
        except Exception as e:
            print(e)

        # db.execute("DROP TABLE Vars;")
        # db.commit()
        # print("Table Vars is dropped")
        try:
            c.execute("""CREATE TABLE Vars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER,
                navn TEXT,
                type INTEGER,
                view INTEGER);""")
        except Exception as e:
            print(e)

        try:
            c.execute("""CREATE TABLE Observation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value INTEGER,
                varid INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);""")
        except Exception as e:
            print(e)

        db.commit()
        return 'Database tables created'
