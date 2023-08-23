import openai


def generate_image(description, ebook_id):
    response = openai.Image.create(
        prompt=description,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    filename = f'output//ebook{ebook_id}.png'
    download_image(image_url, filename)
    return filename


def download_image(url, filename):
    import urllib.request
    r = urllib.request.urlopen(url)
    with open(filename, "wb") as f:
        f.write(r.read())