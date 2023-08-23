from api.dao.database import Database


class EbookDao:

    def __init__(self):
        self.db = Database()

    def create_ebook(self, theme=None) -> dict:
        ebook_id = self.db.insert({'theme': theme})
        ebook = self.db.get(ebook_id)
        ebook['ebook_id'] = ebook_id
        ebook['theme'] = theme
        return ebook

    def get_book(self, ebook_id):
        ebook = self.db.get(ebook_id)
        return dict(ebook)

    def get_ebooks(self):
        ebooks = []
        for d in self.db.table.all():
            d = dict(d)
            ebook = {}
            if 'title' in d.keys():
                ebook['title'] = d['title']
            ebook['id'] = d['ebook_id']
            ebook['theme'] = d['theme']
            ebooks.append(ebook)

        return ebooks

    def set_values(self, values: dict, ebook_id: int):
        ebook = dict(self.db.get(ebook_id))
        for k in values:
            ebook[k] = values[k]
        self.db.update(ebook, int(ebook_id))
        return self.get_book(ebook_id)

    def delete_ebook(self, ebook_id):
        self.db.delete(ebook_id)
