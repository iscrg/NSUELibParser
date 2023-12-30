import ru_local

import os
# import keyboard
from time import sleep

import requests
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver

from io import BytesIO
from PIL import Image

from fpdf import FPDF


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CURRENT_DIR = os.curdir
IMAGES_DIR = 'parser_temp'
STR_TYPE = "<class 'str'>"
GET_ID_ERROR = "Invalid url!"
URL_TEMPLATE = "https://e-lib.nsu.ru/reader/service/SecureViewer/Page/"


def getNumberOfPages(url):
    """
    The function goes to the page of the book and parses the number of pages in the book.
    :param url: URL of the book.
    :return: Number of pages (type: integer).
    """

    try:
        driver = webdriver.Edge()
        driver.get(url)

        sleep(20)

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        span_tag = soup.find('span', {'id': 'number-pages'})

        number_of_pages = span_tag.text.strip()
        number_of_pages = ''.join(char for char in number_of_pages if char.isdigit())

        return int(number_of_pages)

    except Exception as e:
        return e


def saveImage(url, file_name):
    """
    The function saves a photo with a given URL to the "parser_temp" directory.
    :param url: URL of image.
    :param file_name: Name of image file.
    :return: If the operation was successful, True, otherwise error description (type: string).
    """

    try:
        if not os.path.exists(os.path.join(CURRENT_DIR, IMAGES_DIR)):
            os.makedirs(os.path.join(CURRENT_DIR, IMAGES_DIR))

        response = requests.get(url, verify=False)
        image_bytes = BytesIO(response.content)
        image = Image.open(image_bytes)

        file_name = file_name + '.jpg'
        way = os.path.join(CURRENT_DIR, IMAGES_DIR, file_name)
        image.save(way)

        return True

    except Exception as e:
        return e


def parseImages(pages, book_id):
    """
    The function parses pictures and saves them.
    :param pages: Number of pages (type: integer).
    :param book_id: Book ID (type: string).
    :return: If the operation was successful, True, otherwise error description (type: string).
    """

    pages_url = URL_TEMPLATE + book_id

    for i in range(1, pages+1):
        page_url = pages_url + '/' + str(i)
        img_status = saveImage(page_url, str(i))

        if img_status:
            print(ru_local.PARSING, f'{i}/{pages}')
        else:
            return img_status
        sleep(1)

    return True


def getID(url):
    """
    The function extracts the book's ID from the book URL.
    :param url: URL of the book.
    :return: ID of the book (type: string).
    """
    if 'params=' in url:
        bookID = ''
        lBorder = url.find('=') + 1

        for symbol in url[lBorder:]:
            if symbol == '&':
                break
            bookID += symbol

        return bookID

    else:
        return GET_ID_ERROR


def pdfCreator(pages, file_name):
    """
    The function creates a PDF file from existing page files.
    :param pages: Number of pages (type: integer).
    :param file_name: Name of PDF file (type: string).
    :return: If the operation was successful, True, otherwise error description (type: string).
    """

    try:
        pdf = FPDF()

        pdf_width, pdf_height = 210, 297

        for i in range(1, pages+1):
            page_file_name = f'{i}.jpg'
            image_path = os.path.join(CURRENT_DIR, IMAGES_DIR, page_file_name)
            image = Image.open(image_path)

            # Scaling the picture
            pdf_aspect_ratio = pdf_width / pdf_height
            image_aspect_ratio = image.width / image.height
            if pdf_aspect_ratio > image_aspect_ratio:
                image_width = pdf_width
                image_height = pdf_width / image_aspect_ratio
            else:
                image_width = pdf_height * image_aspect_ratio
                image_height = pdf_height
            x = (pdf_width - image_width) / 2
            y = (pdf_height - image_height) / 2

            pdf.add_page()
            pdf.image(image_path, x, y, image_width, image_height)

        pdf_way = os.path.join(CURRENT_DIR, file_name)
        pdf.output(pdf_way)
        return True

    except Exception as e:
        return e


'''
def deleteTemp():
    """
    The function deletes the temporary folder.
    :return: None
    """
    way = os.path.join(CURRENT_DIR, IMAGES_DIR)
    os.remove(way)


def pressAnyKey():
    """
    The function waits for any key to be pressed.
    :return: None
    """
    print(ru_local.PRESS_ANY_KEY)
    keyboard.read_event(suppress=True)
'''


def main():
    url = input(ru_local.TYPE_IN_URL)
    pdf_file_name = input(ru_local.TYPE_IN_PDF_FILE_NAME) + '.pdf'

    pages = getNumberOfPages(url)
    if str(type(pages)) == STR_TYPE:
        message = f'{ru_local.ERROR} {pages}'
        print(message)
        return

    book_id = getID(url)
    if book_id == GET_ID_ERROR:
        message = f'{ru_local.ERROR} {GET_ID_ERROR}'
        print(message)
        return

    parse_status = parseImages(pages, book_id)
    if parse_status:
        pass
    else:
        print(parse_status)
        return

    print(ru_local.CREATING_PDF)
    pdf_status = pdfCreator(pages, pdf_file_name)
    if pdf_status:
        print(ru_local.SUCCESS)
    else:
        message = f'{ru_local.ERROR} {pdf_status}'
        print(message)
        return

    '''
    deleteTemp()
    pressAnyKey()
    '''


if __name__ == "__main__":
    main()
