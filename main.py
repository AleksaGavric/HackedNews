import json
from bs4 import BeautifulSoup
from fastapi import FastAPI
import openai
import requests, dotenv, os
from readability import Document

dotenv.load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_KEY

MODEL = "gpt-3.5-turbo"

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


def get_hackernews_top_stories():
    response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")

    if response.status_code != 200:
        raise Exception(
            "[ERROR] Cannot establish connection to HackerNews, please try again later."
        )

    top_stories = response.json()[:10]

    # get link for each story
    hn_top_stories = []

    for story_id in top_stories:
        story = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        ).json()

        hn_top_stories.append(
            {
                "title": story["title"],
                "url": story["url"],
            }
        )

    return hn_top_stories


def get_url_text(url):
    response = requests.get(url)

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
            {
                "role": "system",
                "content": "Please provide a detailed and realistic abstractive summary of the following content:",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )

    summary_text = payload["choices"][0]["message"]["content"]

    return summary_text
