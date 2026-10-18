from urllib.parse import urljoin
from bs4 import BeautifulSoup


def parse_article(html: str, page_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("article.article-body")   # only the real article
    if body is None:
        raise ValueError("article body not found")

    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else page_url

    chunks = []
    heading, lines, images = title, [], []

    def flush():
        text = "\n".join(lines).strip()
        if text:
            chunks.append({"heading": heading, "text": text, "images": images})

    for el in body.find_all(["h2", "h3", "h4", "p", "li", "img"]):
        if el.name in ("h2", "h3", "h4"):
            flush()                                   # close the previous section
            heading, lines, images = el.get_text(" ", strip=True), [], []
        elif el.name == "img":
            src = el.get("src") or el.get("data-src")
            if src and not src.startswith("data:") and not src.endswith("/hit"):
                images.append({
                    "src": urljoin(page_url, src),
                    "alt": el.get("alt", ""),
                    "context": lines[-1][:200] if lines else heading,
                })
        else:
            if el.name == "p" and el.find_parent("li"):
                continue                              # avoid counting text twice
            text = el.get_text(" ", strip=True)
            if text and not text.startswith("Link:") and text != title:
                lines.append(text)
    flush()
    return {"title": title, "chunks": chunks}
