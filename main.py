from bs4 import BeautifulSoup
from fastapi import FastAPI
import openai
import requests, dotenv, os
from readability import Document
from transformers import GPT2Tokenizer

dotenv.load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_KEY

MODEL = "gpt-3.5-turbo"
MODEL_TEMPERATURE = 0.1
CONTEXT_PROMPT = "Please provide a detailed and realistic abstractive summary of the following content:\n"

app = FastAPI(
    title="Daigest",
    version="1.0",
    summary="HackerNews Daily Daigest",
)


@app.get("/")
def read_root():
    text = get_url_text("https://blog.jakoblind.no/aws-lambda-github-actions/")
    summary = summarize(text)

    return summary


def get_url_text(url):
    response = requests.get(url)

    print(response)

    if response.status_code != 200:
        raise Exception(
            "[ERROR] Cannot establish connection to URL, please try again later."
        )

    CONTENT_TYPE = response.headers["Content-Type"]

    if "html" not in CONTENT_TYPE:
        raise Exception(f"[ERROR] Unsupported website content type.")

    doc = Document(response.content)
    soup = BeautifulSoup(doc.summary(), "html.parser")
    html_soup = soup.find_all(text=True)

    blacklist = [
        "[document]",
        "noscript",
        "header",
        "html",
        "meta",
        "head",
        "input",
        "script",
        "style",
    ]

    text = ""

    for page_el in html_soup:
        if page_el.parent.name not in blacklist:
            text += "{} ".format(page_el)

    if not len(text):
        raise Exception("[ERROR] No text content found.")

    return text


def summarize(text):
    payload = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": CONTEXT_PROMPT},
            {
                "role": "user",
                "content": text,
            },
        ],
    )

    summary_text = payload["choices"][0]["message"]["content"]

    return summary_text
