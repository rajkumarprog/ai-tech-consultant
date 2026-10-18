
import httpx
import xml.etree.ElementTree as ET

url = "https://support.brilliantdirectories.com/support/sitemap.xml"
response = httpx.get(url, timeout=30, follow_redirects=True)

root = ET.fromstring(response.content)
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}

pages = []

for url_tag in root.findall("s:url", ns):
    loc = url_tag.find("s:loc", ns).text
    lastmod = url_tag.find("s:lastmod", ns)
    pages.append((loc, lastmod.text if lastmod is not None else None))

print("Total pages:", len(pages))

article_pages = [
    (loc, lm) for loc, lm in pages if "/articles/" in loc
]

print("Total:", len(pages), "Articles:", len(article_pages))

for loc, lm in article_pages[:3]:
    print(loc)
from bs4 import BeautifulSoup

# 1. Take the first article page found in the sitemap
test_url = article_pages[0][0]
print("Testing:", test_url)

# 2. Download it (same idea as the sitemap download)
page = httpx.get(test_url, timeout=30, follow_redirects=True)
soup = BeautifulSoup(page.text, "html.parser")

# 3. Pull out the pieces we decided to keep
title = soup.find("h1")
print("Title:", title.get_text(strip=True) if title else "NOT FOUND")
print("Headings:", [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])][:5])
print("Paragraphs:", len(soup.find_all("p")))
print("Images:", [img.get("src") for img in soup.find_all("img")][:3])
# 3. Pull out the pieces we decided to keep
title = soup.find("h1")
print("Title:", title.get_text(strip=True) if title else "NOT FOUND")
print("Headings:", [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])][:5])
print("Paragraphs:", len(soup.find_all("p")))
print("Images:", [img.get("src") for img in soup.find_all("img")][:3])

page.raise_for_status()
title = soup.find("h1")
print("Title:", title.get_text(" ", strip=True) if title else "NOT FOUND")
print("Headings:", [h.get_text(" ", strip=True) for h in soup.find_all(["h2", "h3"])[:5]])
print("Paragraphs:", len(soup.find_all("p")))
print("Images:", [img.get("src") for img in soup.find_all("img")[:3]])
