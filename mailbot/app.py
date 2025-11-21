from flask import Flask
import requests
import feedparser
import os
from email.mime.text import MIMEText
import smtplib

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PW = os.environ.get("EMAIL_PW")

def fetch_rss():
    feeds = [
        "https://www.zdnet.co.kr/news/news_xml.asp?ct=0000",
        "https://rss.etnews.com/Section902.xml"
    ]
    items = []
    for f in feeds:
        parsed = feedparser.parse(f)
        for e in parsed.entries[:5]:
            items.append({"title": e.title, "link": e.link})
    return items

def summarize_with_gpt(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    prompt = f"""
다음 IT 뉴스들을 5줄로 요약하고 키워드 5개 뽑아줘:

{text}
"""
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

def send_email(summary):
    msg = MIMEText(summary, "html")
    msg["Subject"] = "Daily IT Trend"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PW)
    server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
    server.quit()

@app.route("/")
def main():
    items = fetch_rss()
    text = "\n".join([f"- {i['title']} ({i['link']})" for i in items])
    summary = summarize_with_gpt(text)
    send_email(summary)
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
