import httpx
from bs4 import BeautifulSoup

url = "https://support.brilliantdirectories.com/support/solutions/articles/5000558357-can-i-send-a-mass-email-campaign-using-brilliant-directories-"

response = httpx.get(url, timeout=30, follow_redirects=True)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

candidates = [
    "article.article-body",
    "#article-body",
    ".article-body",
    "article",
    "main",
    ".article-content",
    ".fw-content",
]

for selector in candidates:
    element = soup.select_one(selector)

    if element:
        text = element.get_text(" ", strip=True)
        print(f"\n{selector}: FOUND")
        print("Text length:", len(text))
        print("Preview:", text[:150])
    else:
        print(f"\n{selector}: not found")
