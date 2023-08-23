
# EBook Creator API

The EBook Creator API harnesses the capabilities of AI to create and manage eBooks. Integrated with OpenAI and Google Custom Search Engine, this API offers a seamless way to produce content based on various user inputs.

## API Endpoints:

- **`/api/ebook`**: Endpoint to create an eBook identifier with its theme.
- **`/api/ebooks`**: Fetch a list of all generated eBooks.
- **`/api/ebook/generate/full`**: Generate a full complete ebook by the theme(DALL-E).
- **`/api/ebook/<ebook_id>`**: Retrieve, update or delete a specific eBook using its ID.
- **`/api/ebook/<ebook_id>/image`**: Retrieve or generate the cover image of the book.
- **`/api/ebook/<ebook_id>/table-of-contents`**: Generates the table of contents of a ebook and title.
- **`/api/ebook/<ebook_id>/chapter/<chapter_number>`**: Generates or gets a chapter.
- **`/api/ebook/<ebook_id>/chapter/<chapter_number>/research`**: Generates or gets the research of a chapter.
- **`/api/ebook/download/<ebook_id>`**: Download the eBook in your desired format(docx or pdf).
- **`/api/ebook/generate/<ebook_id>`**: Generate a ebook with pre-generated content.

For detailed information on how to use each endpoint, including required parameters and response formats, please refer to the Swagger documentation provided with the API.

## Setup:

1. Ensure your environment variables are properly set:
   ```
   OPENAI_API_KEY=your_openai_key
   GOOGLE_CSE_ID=your_google_cse_id
   GOOGLE_API_KEY=your_google_api_key
   DEBUG=True_or_False
   ```

2. Install the necessary packages (as outlined in your project's requirements).

3. Run the API:
   ```
   python app.py
   ```

## CONTRIBUTION

Feel free to contribute, raise issues, or provide feedback. Let's make eBook creation smarter and more accessible to all!

## LICENSE
This project is under MIT license.
