import re
from bs4 import BeautifulSoup

with open("c:/workspace/VSCodeProjects/demodev/naver-stock/stock_market.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
checkboxes = soup.find_all('input', {'name': 'fieldIds'})

fields = []
for cb in checkboxes:
    val = cb.get('value')
    label = soup.find('label', {'for': cb.get('id')})
    label_text = label.text if label else ""
    fields.append((label_text, val))

for text, val in fields:
    print(f"{text}: {val}")
