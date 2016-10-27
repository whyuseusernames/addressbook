import sqlite3

class Database:
    def __init__(self):
        self.db = sqlite3.connect("test.db", check_same_thread=False)
        self.db.execute(''' create table if not exists ADDRESSBOOK (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            NAME CHAR(100) NOT NULL, ADDRESS CHAR(100), PHONE CHAR(22)); ''')
        self.cursor = self.db.cursor()
 
    def dump(self):
        cur = self.cursor.execute('select * from ADDRESSBOOK')
        return {'response': self.format_row(cur)}
        
    def format_row(self, cur):
        rows = [{'id': row[0], 'name': row[1], 'address': row[2], 'phone': row[3]} for row in cur]
        if len(rows) < 1:
            return [{'id': 'does not exist'}]
        else:
            return rows

    def update(self, id=None, params=None):
        check = self.get_by_field(field="id", param=id)[0]
        if check['id'] == 'does not exist':
            return check

        if id and isinstance(params, dict):
            for key, value in params.iteritems(): 
                query = "UPDATE ADDRESSBOOK SET {}=? WHERE ID=?".format(key.upper()) 
                if any(key.lower() in v for v in ('name', 'address', 'phone')):
                    self.cursor.execute(query, (value, str(id)))
                    self.db.commit()
                    resp = self.get_by_field(field="id", param=str(id))[0] 
                    if resp[key.lower()] != value:
                        return {'response': 'failure to update entry'} 
            return {'response': 'success'}    
        return {'response': 'failed, invalid params'}

    def insert(self, name=None, address=None, phone=None):
        if all([name, address, phone]): 
            if not self.exist(name=name, address=address, phone=phone):
                self.cursor.execute('''INSERT INTO ADDRESSBOOK (NAME, ADDRESS, PHONE) 
                                           VALUES (?, ?, ?)''', (name, address, phone))

                self.db.commit()
                if self.exist(name=name, address=address, phone=phone):
                    return { 'response': 'success' }
                else:
                    return { 'response': 'failure' } 
            else:
                return { 'response': 'entry exists' }
        else:
            return { 'response': 'invalid or incomplete data' } 

    def get_by_field(self, field=None, param=None):
        query = "SELECT * from ADDRESSBOOK where {}=? COLLATE NOCASE".format(field.upper())
        try:
            cur = self.cursor.execute(query, (param,)) 
        except Exception as e:
            return {'response': e.message}
        return self.format_row(cur)

    def delete(self, id):
        check = self.get_by_field(field="id", param=id)[0]
        if check['id'] == 'does not exist':
            return check
        data = "SELECT * from ADDRESSBOOK WHERE ID={};".format(id)
        cur = self.db.execute(data)
        (id, name, address, phone) = cur.fetchall()[0]
        if all([id, name, address, phone]):
            query = "DELETE from ADDRESSBOOK WHERE ID={};".format(id)
            self.db.execute(query)
            self.db.commit()
            if self.exist(name=name, address=address, phone=phone):
                return { 'response': 'delete failure, data still in db' }
            else:
                return { 'response': 'success' }

    def exist(self, name=None, address=None, phone=None):
        query = """SELECT * from ADDRESSBOOK where NAME='{}' COLLATE NOCASE 
                       AND ADDRESS='{}' COLLATE NOCASE 
                       AND PHONE='{}';""".format(name, address, phone)
        cur = self.cursor.execute(query)
        if len(cur.fetchall()) > 0:
            return True
        return False

    def search(self, content):
        key = content.keys()
        if len(key) == 1 and key[0] in ["name", "address", "phone"]:
            key = key[0]
            value = content.values()[0]
            query = "SELECT * from ADDRESSBOOK where {} LIKE ?".format(key)
            cur = self.cursor.execute(query, ('%'+value+'%',)) 
            cur = cur.fetchall()
            if len(cur) < 1:
                return {'response': 'no search results'}
            return {'response': self.format_row(cur)}
        else:
            return {'response': 'invalid search'} 

    def close(self):
        self.db.close()



