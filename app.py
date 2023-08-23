import os

from dotenv import load_dotenv
from flask import Flask, request, send_file
from flask_restx import Api, Resource, fields, reqparse

from api.chapter_creator import ChapterCreator
from api.ebook_creator import EbookCreator

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv(key="OPENAI_API_KEY")
os.environ["GOOGLE_CSE_ID"] = os.getenv(key="GOOGLE_CSE_ID")
os.environ["GOOGLE_API_KEY"] = os.getenv(key="GOOGLE_API_KEY")
app = Flask(__name__)
api = Api(app, version='1.0', title='EBook Creator API', description='A simple EBook Creator API')

ns = api.namespace('api', description='EBook operations')
parser = reqparse.RequestParser()
parser.add_argument('theme', type=str, help='Theme of the book', required=True)
parser.add_argument('type_doc', type=str, help='Type of the document', required=False)
parser.add_argument('topics', type=str, help='Topics of the book', required=False)
parser.add_argument('return_chapters', type=str, help='If returns or not chapter texts', required=False)
parser.add_argument('description_cover', type=str, help='The description of the cover image to generate',
                    required=False)

table_of_contents_model = api.model('TableOfContents', {
    'table_of_contents': fields.List(fields.String, required=True, description='Table of contents')
})

researches_model = api.model('ListResearch', {
    'research': fields.String(required=True, description='Research of the chapter'),
})

image_model = api.model('Image', {
    'url': fields.String(required=True, description='The image URL'),
})

document_model = api.model('Document', {
    'document': fields.String(required=True, description='The document URL'),
})

chapter_model = api.model('Chapter', {
    'number': fields.Integer(required=True, description='The chapter number'),
    'text': fields.String(required=True, description='The chapter text'),
    'title': fields.String(required=True, description='The chapter title'),
})

ebook_model = api.model('Ebook', {
    'id': fields.String(required=False, description='The reference of the book'),
    'theme': fields.String(rquired=False, description='The theme of the book'),
    'title': fields.String(rquired=False, description='The title of the book'),
    'chapters': fields.List(fields.Nested(chapter_model), required=False, description='The list of chapters'),
    'table_of_contents': fields.List(fields.String, required=False, description='The table of contents'),
    'cover_image': fields.String(required=False, description='The cover image')
})

ebooks_model = api.model('Ebooks', {
    'id': fields.String(required=False, description='The reference of the book'),
    'theme': fields.String(rquired=False, description='The theme of the book'),
    'title': fields.String(rquired=False, description='The title of the book'),
})


def download_file(ebook_id, type_doc):
    mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' if type_doc == 'docx' else 'application/pdf'
    return send_file(os.getcwd() + f"/output/ebook{ebook_id}.{type_doc}", as_attachment=True, mimetype=mimeType)


@ns.route('/ebook/<ebook_id>/chapter/<chapter_number>/research')
@api.doc(params={'ebook_id': 'The ID of the ebook', 'chapter_number': 'The chapter number to generate the research'})
class EBookResearch(Resource):
    '''Generate the research of the chapter based on the sources'''

    @ns.doc('generate_research')
    @ns.marshal_with(researches_model, code=201)
    def post(self, ebook_id, chapter_number):
        chapter_creator = ChapterCreator()
        research = chapter_creator.generate_research(ebook_id, chapter_number)
        return {"research": research}, 201

    @ns.marshal_with(researches_model, code=300)
    def get(self, ebook_id, chapter_number):
        chapter_creator = ChapterCreator()
        research = chapter_creator.get_research(ebook_id, chapter_number)
        return {"research": research}, 300


@ns.route('/generate/ebook/<ebook_id>/table-of-contents')
@api.doc(params={'ebook_id': 'The ID of the ebook', 'topics': 'The topics tu put on the book'})
class EBookTableOfContents(Resource):
    @ns.doc('generate_table_of_contents')
    @ns.marshal_with(table_of_contents_model, code=201)
    def post(self, ebook_id):
        '''Generate table of contents of the ebook and title'''
        topics = request.args.get('topics')
        ebook = EbookCreator().gen_table_of_contents(ebook_id, topics)
        return {'table_of_contents': ebook['table_of_contents']}, 201


@ns.route('/ebook/<ebook_id>/chapter/<chapter_number>')
@api.doc(params={'ebook_id': 'The ID of the ebook', 'chapter_number': 'The chapter number to generate'})
class EBookChapter(Resource):
    @ns.doc('generate_chapter')
    @ns.marshal_with(chapter_model, code=201)
    def post(self, ebook_id, chapter_number):
        '''Generated a chapter based on research'''
        chapter_creator = ChapterCreator()
        chapter = chapter_creator.generate_chapter(ebook_id, chapter_number)
        return chapter, 201

    def get(self, ebook_id, chapter_number):
        '''Generated a chapter based on research'''
        chapter_creator = ChapterCreator()
        chapter = chapter_creator.get_chapter(ebook_id, chapter_number)
        return chapter, 200


@ns.route('/update/ebook?<ebook_id>')
@api.doc(params={'ebook_id': 'The ID of the ebook'})
class UpdateEbook(Resource):
    '''Updates any value on a ebook'''

    @ns.doc('update_ebook')
    @ns.expect(ebook_model)
    def put(self, ebook_id):
        '''Faz update de um ebook'''
        data = request.get_json(force=True)
        ebook = EbookCreator().set_values(ebook_id, data)
        return {'id': ebook.id}, 204


@ns.route('/create/ebook')
@api.doc(params={'theme': 'Theme of the ebook'})
class CreateEbook(Resource):
    @ns.doc('create_ebook')
    @ns.marshal_with(ebook_model, code=201)
    def post(self):
        '''Create a to build ebook with his theme and returns its id'''
        args = parser.parse_args()
        theme = args.get('theme')
        eb = EbookCreator()
        ebook = eb.create_ebook(theme)
        return {'id': ebook['ebook_id'], 'theme':theme}, 201


@ns.route('/generate/ebook/<ebook_id>')
@api.doc(params={'ebook_id': 'The ID of the ebook'})
class GenerateEBook(Resource):
    '''Generates a ebook by the previous saved data on it and returns it'''

    @ns.doc('generate_ebook')
    def post(self, ebook_id):
        eb = EbookCreator()
        eb.generate_ebook(ebook_id)
        return download_file(ebook_id, 'docx')


@ns.route('/generate/ebook/full')
@api.doc(params={'theme': 'Theme of the ebook'})
class GenerateEBookFull(Resource):
    '''Generates a complete ebook from scratch based on the theme chosen and returns it'''

    content_type = 'text/plain'

    @ns.doc('/generate_ebook_full')
    def post(self):
        args = parser.parse_args()
        theme = args.get('theme')
        print("Theme" + theme)
        eb = EbookCreator()
        ebook_id = eb.generate_ebook(None, theme)
        return download_file(ebook_id, 'docx')


@ns.route('/ebook/<ebook_id>/image')
@api.doc(
    params={'ebook_id': 'The ID of the ebook'})
class GenerateEbookImage(Resource):
    '''Get the ebooks image cover'''
    content_type = 'image/png'

    def get(self, ebook_id):
        return send_file(os.getcwd() + f"/output/ebook{ebook_id}.png", as_attachment=True, mimetype="image/png")


@ns.route('/generate/ebook/<ebook_id>/image')
@api.doc(
    params={'ebook_id': 'The ID of the ebook', 'description_image': 'The description of the cover image to generate'})
class GenerateEbookImage(Resource):
    '''Generates a cover image for the ebook'''
    content_type = 'image/png'

    @ns.doc('generate_image_cover')
    def post(self, ebook_id):
        '''Gera a imagem de capa do ebook'''

        description_image = request.args.get('description_image')
        EbookCreator().generate_cover(ebook_id, description_image)
        return send_file(os.getcwd() + f"/output/ebook{ebook_id}.png", as_attachment=True, mimetype="image/png")


@ns.route('/ebook/download/<ebook_id>')
@api.doc(params={'ebook_id': 'The ID of the ebook', 'type_doc': 'The type of the document (pdf/docx)'})
class DownloadEbook(Resource):
    '''Returns a ebook on the format specified: json/pdf/docx'''
    content_type = 'text/plain'

    # @ns.marshal_with(document_model, code=201)
    def get(self, ebook_id):
        '''Retorna um doc/pdf/json do ebook pelo seu id'''
        type_doc = request.args.get('type_doc')
        EbookCreator().get_ebook(ebook_id, type_doc)
        return download_file(ebook_id, type_doc)


@ns.route('/ebook/<ebook_id>')
@api.doc(params={'ebook_id': 'The ID of the ebook', 'return_chapters': 'If you want to return teh text of chapters'})
class GetEbook(Resource):
    '''Returns a ebook on the format specified: json/pdf/docx'''

    # @ns.marshal_with(document_model, code=201)
    def get(self, ebook_id):
        '''Retorna um json do ebook pelo seu id'''
        return_chapters = request.args.get('return_chapters')
        ebook = EbookCreator().get_ebook(ebook_id, 'json', return_chapters)
        return ebook, 200

    def delete(self, ebook_id):
        '''Retorna um json do ebook pelo seu id'''
        ebook = EbookCreator().delete_ebook(ebook_id)
        return None, 204


@ns.route('/ebooks')
@api.doc()
class GetEbooks(Resource):
    '''Returns a list of all ebooks'''

    @ns.marshal_with(ebooks_model, code=200)
    def get(self):
        '''Returns a list of all ebooks'''
        ebooks = EbookCreator().get_all()
        return ebooks, 200


# Error handling
@app.errorhandler(500)
def handle_500_error(e):
    return jsonify(error=str(e)), 500

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify(error=str(e)), 400

if __name__ == '__main__':
    # Using environment variables for configuration
    app.run(debug=os.getenv("DEBUG", "False").lower() == "true")
