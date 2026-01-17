import os
from dotenv import load_dotenv
import numpy as np
from google import genai
from PIL import Image


load_dotenv()

client = genai.Client()

def show_and_tell(client, img:np.array):
    """
    Describes the image returned to function.
    """

    # convert np image to pillow

    img = Image.fromarray(img)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=["Give a very detailed discription of the image given to you. Include anything that could be beneficial like brands or logos and sizes of the item.", img]

    )

    return response.text


def extract_search_terms_from_description(description):
    """
    Converts image description into compact search term.
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="Given the very detailed description, output a more compact description suitable for search purposes in a search engine"
    )

    return response.text