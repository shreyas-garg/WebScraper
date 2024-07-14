from bs4 import BeautifulSoup
from requests import get

headers = {
    "user-agent": "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4"
}

def int_extractor(string):
    int_string = ""

    for ch in string:
        if ch == "." and int_string:
            break

        if not ch.isdigit():
            continue

        int_string += ch

    return int(int_string)

def fetch(url, headers):
    resp = get(url, headers=headers)
    while resp.status_code != 200:
        resp = get(url, headers=headers)
    
    return resp.text

def scrape(url, item, headers, scrape_data):
    html = fetch(url + item, headers=headers)
    soup = BeautifulSoup(html, "html.parser")

    products = soup.find_all(
        scrape_data["product"][0],
        scrape_data["product"][1]
    )

    results = []

    for product in products:
        name = product.find(scrape_data["name"][0], scrape_data["name"][1])
        price = product.find(scrape_data["price"][0], scrape_data["price"][1])
        link = product.find("a", href=True)

        if not (name and price and link):
            continue

        results.append({
            "name": name.get_text(),
            "price": int_extractor(price.get_text()),
            "link": link["href"],
            "source": scrape_data["source"]
        })
    
    return results

def scrape_amazon(item, headers):
    return scrape(
        "https://www.amazon.in/s?k=",
        item,
        headers=headers,
        scrape_data={
            "product": ["div", {"class": "s-result-item"}],
            "name": ["span", "a-text-normal"],
            "price": ["span", "a-offscreen"],
            "source": "Amazon"
        }
    )

def scrape_snapdeal(item, headers):
    return scrape(
        "https://www.snapdeal.com/search?keyword=",
        item,
        headers=headers,
        scrape_data={
            "product": ["div", {"class": "product-tuple-listing"}],
            "name": ["p", "product-title"],
            "price": ["span", "product-price"],
            "source": "Snapdeal"
        }
    )

def scrape_all(item, headers):
    results = []
    results.extend(scrape_amazon(item, headers=headers))
    results.extend(scrape_snapdeal(item, headers=headers))

    results.sort(key=lambda product: product["price"])

    return results

def search(headers):
    item = input("Search for item: ")
    results = scrape_all(item, headers=headers)
    
    return results

def main():
    results = search(headers=headers)

    for product in results:
        name = product["name"]
        price = product["price"]
        source = product["source"]

        price = f"Rs. {price:,}"

        print(f"{name} - {price} ({source})")

main()

