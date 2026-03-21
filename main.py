import logging
import sqlite3
from contextlib import closing

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "page_views.db"


class PageView(BaseModel):
    url: str
    title: str
    lang: str
    text: str
    headers: str
    timestamp: str


class LlmRequest(BaseModel):
    prompt: str


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                lang TEXT NOT NULL,
                text TEXT NOT NULL,
                headers TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
            """
        )
        conn.commit()


def save_page_view(page_view: PageView):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO page_views (url, title, lang, text, headers, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                page_view.url,
                page_view.title,
                page_view.lang,
                page_view.text,
                page_view.headers,
                page_view.timestamp,
            ),
        )
        conn.commit()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database initialized: %s", DB_PATH)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/page-view")
def page_view(page_view: PageView):
    logger.info("=" * 60)
    logger.info("URL:       %s", page_view.url)
    logger.info("Title:     %s", page_view.title)
    logger.info("Lang:      %s", page_view.lang)
    logger.info("Timestamp: %s", page_view.timestamp)
    logger.info("Text:      %s...", page_view.text[:100])
    logger.info("Headers:   %s...", page_view.headers[:100])
    logger.info("=" * 60)

    save_page_view(page_view)
    logger.info("Page view saved to database")

    return {"status": "ok"}


@app.post("/request")
def llm_proxy(req: LlmRequest):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": req.prompt,
            "system": "Отвечай на русском и будь токсичен!",
            "temperature": 0.9,
            "stream": False,
        },
    )
    return response.json().get("response")


@app.get("/history")
def history():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        rows = conn.execute("SELECT headers FROM page_views ORDER BY id ASC").fetchall()
        prompt_text = "\n".join(row[0] for row in rows)

    deepseek_response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": f"Дай сводку посещенных сайтов: {prompt_text}",
            "system": "Отвечай на русском и будь токсичен!",
            "stream": False,
        },
    ).json()
    text_response = deepseek_response.get("response") or deepseek_response.get(
        "message", {}
    ).get("content")

    prompt_response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": f"Short prompt for visualisation (up to 15 words): {text_response}",
            "stream": False,
        },
    ).json()

    sd_prompt = prompt_response.get("response") or prompt_response.get(
        "message", {}
    ).get("content")

    sd_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    sd_payload = {"prompt": sd_prompt, "steps": 20, "width": 512, "height": 512}

    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        sd_response = requests.request(
            method="POST", url=sd_url, json=sd_payload, headers=headers
        ).json()

        image_base64 = sd_response.get("images", [None])[0]

        if not image_base64:
            return {"error": "SD returned no image", "debug": sd_response}

        return {"text": text_response, "image": f"data:image/png;base64,{image_base64}"}
    except Exception as e:
        return {"error": str(e)}
