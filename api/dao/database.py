from tinydb import TinyDB, Query, where
import json


class Database:

    def __init__(self):
        db = TinyDB('./db/db.json')
        self.table = db.table('ebooks')
        
    def __enter__(self):
       return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def insert(self, data):
        return self.table.insert(data)

    def update(self, values, d_id):
        self.table.update(values, doc_ids=[d_id])

    def delete(self, d_id):
        file = None
        with open("db//db.json", "r") as f:
            file = f.read()
        json_obj = json.loads(file)
        ebooks = dict(json_obj)
        ebooks['ebooks'].pop(d_id)
        with open("db//db.json", "w") as f:
            f.write(json.dumps(ebooks))

    def get(self, d_id):
        return self.table.get(doc_id=d_id)
