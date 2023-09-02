import json

from api.dao.ebook_dao import EbookDao
from api.creator import Creator
from api.chapter_creator import ChapterCreator
import api.document_creator as document_creator
from api.image_gen import generate_image
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo


def get_ebook_json(ebook, return_chapters):
    ebook_response = {}
    for key in ebook.keys():
        if key not in ['research', 'chapters']:
            ebook_response[key] = ebook[key]
    if 'chapters' in ebook.keys() and return_chapters:
        ebook_response['chapters'] = []
        for chapter in ebook['chapters'].keys():
            chapter_response = {}
            for key in ebook['chapters'][chapter].keys():
                chapter_response[key] = ebook['chapters'][chapter][key]
            chapter_response['research'] = ebook['research'][chapter]
            ebook_response['chapters'].append(chapter_response)
    return ebook_response


class EbookCreator(Creator):

    def __init__(self):
        super().__init__()
        self.eb = EbookDao()
        self.cc = ChapterCreator()

    def get_ebook(self, ebook_id, type='json', return_chapters=False):
        if type not in ['docx', 'pdf', 'json']:
            raise Exception('Invalid type')
        ebook = self.eb.get_book(ebook_id)
        ebook['sources'] = self.get_sources(ebook['theme'])
        if type == 'json':
            return get_ebook_json(ebook, return_chapters)
        elif type == 'docx':
             document_creator.create_docx(ebook, ebook_id)
        else:
             document_creator.convert_docx_to_pdf(ebook, ebook_id)


    def gen_table_of_contents(self, ebook_id, topics=[]):
        ebook = self.eb.get_book(ebook_id)
        agent = self.get_zero_shot_agent([self.tool_search()])

        response = agent.run(self.get_prompt('table_of_contents').replace('{theme}', ebook["theme"])
                             .replace("{topics}", str(topics)))
        response = self.extract_json_from_text(response)
        return self.eb.set_values(response, ebook_id)

    def create_ebook(self, theme):
        ebook = self.eb.create_ebook(theme)
        self.eb.set_values(ebook, ebook['ebook_id'])
        ebook['theme'] = theme
        return ebook

    def set_values(self, values, ebook_id=None):
        self.eb.set_values(values, ebook_id)

    def generate_ebook(self, ebook_id=None, theme=None):
        ebook = None
        if ebook_id is None:
            ebook = self.eb.create_ebook(theme)
            ebook_id = ebook['ebook_id']
            ebook['chapters'] = {}
            self.set_values(ebook, ebook_id)
        else:
            ebook = self.eb.get_book(ebook_id)
        if 'table_of_contents' not in ebook.keys():
            ebook = self.gen_table_of_contents(ebook_id)
        self.generate_chapters(ebook, ebook_id)
        ebook['sources'] = self.get_sources(ebook['theme'])
        document_creator.create_docx(ebook, ebook_id)
        return ebook_id

    def generate_chapters(self, ebook, ebook_id):
        if len(ebook['chapters'].keys()) != len(ebook['table_of_contents']):
            i = 1
            for chapter in ebook['table_of_contents']:
                if len(ebook['chapters'].keys()) != i:
                    ebook['chapters'][str(i)] = self.cc.generate_chapter(ebook_id, i)
                i = i + 1

    def generate_cover(self, ebook_id, desc_image=None):
        ebook = self.eb.get_book(ebook_id)
        if desc_image is None:
            desc_image = self.gpt3.predict("Make a brief detailed description for the image cover of the book in one prhase, make an abstract concept related to the theme, without text, the book title: "+ebook['title'])
        image = generate_image(desc_image, ebook_id)
        ebook['cover'] = image
        self.eb.set_values(ebook, ebook_id)

    def get_all(self):
        return self.eb.get_ebooks()

    def delete_ebook(self, ebook_id):
        ebook = self.eb.get_book(ebook_id)
        if 'research' in ebook.keys():
            docs = self.get_sources(ebook['theme'])
            self.vectorstore.delete(docs)
        self.eb.delete_ebook(ebook_id)

    def get_sources(self, theme: str):
        metadata_field_info = [
            AttributeInfo(
                name="source",
                description="The url source of the text",
                type="string",
            ),
            AttributeInfo(
                name="theme",
                description="The theme of the research",
                type="string",
            )
        ]

        retriever = SelfQueryRetriever.from_llm(
            self.gpt4, self.vectorstore, "Research about a theme", metadata_field_info, verbose=True
        )
        docs = retriever.get_relevant_documents(theme)
        results = []
        for d in docs:
            results.append(d.metadata['source'])

        return results

