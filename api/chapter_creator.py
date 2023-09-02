from api.dao.ebook_dao import EbookDao
from api.creator import Creator
from langchain.prompts.chat import HumanMessage
import json


def verify_table_of_contents(ebook):
    if 'table_of_contents' not in ebook.keys():
        raise Exception('Table of contents not found')
    return ebook['table_of_contents']


def get_chapter(chapter_number, ebook):
    index = int(chapter_number)-1
    table_of_contents = verify_table_of_contents(ebook)
    chapter = table_of_contents[index]
    return chapter


class ChapterCreator(Creator):

    def __init__(self):
        super().__init__()
        self.eb = EbookDao()

    def generate_research(self, ebook_id, chapter_number) -> dict:
        chapter_number = str(chapter_number)
        ebook = self.eb.get_book(ebook_id)
        chapter = get_chapter(chapter_number, ebook)
        if 'research' not in ebook.keys():
            ebook['research'] = {}
        agent = self.get_zero_shot_agent([self.tool_search()])
        response = agent.run(self.get_prompt('research').replace('{chapter_name}', chapter['chapter_name']).replace('{topics}', str(chapter['list_of_topics'])))
        ebook['research'][chapter_number] = response
        self.eb.set_values(ebook, ebook_id)
        return response

    def generate_chapter(self, ebook_id, chapter_number):
        ebook = self.eb.get_book(ebook_id)
        chapter_number = str(chapter_number)
        if 'research' not in ebook.keys() or chapter_number not in ebook['research'].keys():
            res = self.generate_research(ebook_id, chapter_number)
            ebook = self.eb.get_book(ebook_id)
            ebook['research'][chapter_number] = res
        chapter_name = get_chapter(chapter_number, ebook)['chapter_name']
        research = ebook['research'][chapter_number]
        response = self.gpt3(messages=[HumanMessage(content=self.get_prompt('chapter')
                                                    .replace('{chapter_name}', chapter_name)
                                                    .replace('{research}', research)
                                                    .replace('{theme}', ebook['theme'])
                                                    )],)
        if 'chapters' not in ebook.keys():
            ebook['chapters'] = {}
        response = {'text': response.content, 'title': chapter_name, "number": chapter_number}
        ebook['chapters'][chapter_number] = response
        self.eb.set_values(ebook, ebook_id)
        return response

    def get_chapter(self, ebook_id, chapter_number):
        ebook = self.eb.get_book(ebook_id)
        return ebook['chapters'][chapter_number]

    def get_research(self, ebook_id, chapter_number):
        ebook = self.eb.get_book(ebook_id)
        return ebook['research'][chapter_number]
