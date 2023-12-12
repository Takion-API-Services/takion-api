from tls_client import Session
from takion_api import TakionAPIDatadome


def load_page(session: Session, url: str):
    headers = {
        "authority": url.split("/")[2],
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-GB,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Google Chrome";v="110", "Chromium";v="110", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    return session.get(url, headers=headers)


if __name__ == "__main__":
    takion_api = TakionAPIDatadome(
        api_key="TAKION_API_XXXXXX",
    )
    session = Session(
        "chrome_110", 
        header_order=[
            'Host', 'Connection', 'Content-Length', 
            'sec-ch-ua', 'sec-ch-ua-platform', 
            'sec-ch-ua-mobile', 'User-Agent', 
            'Content-Type', 'Accept', 'Origin', 
            'Sec-Fetch-Site', 'Sec-Fetch-Mode', 
            'Sec-Fetch-Dest', 'Referer', 'Accept-Encoding', 
            'Accept-Language'
        ]
    )
    url = "https://www.footlocker.pt/en/product/~/314206535404.html"
    
    response = load_page(session, url)
    if not takion_api.is_challenge(response):
        print("Page loaded successfully")
        exit(0)
    
    print(f"Got a response with status code {response.status_code} without the cookie")

    print("Solving challenge...")
    challenge_url = takion_api.get_challenge_url(
        url,
        response,
        session.cookies.get_dict().get("datadome")
    )

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "none",
        "Connection": "keep-alive",
        "Referer": "https://www.footlocker.pt/",
        "Sec-Fetch-Dest": "iframe",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="110", "Chromium";v="110", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\""
    }
    response = session.get(challenge_url, headers=headers)

    data = takion_api.solve_challenge(
        response
    )
    res = session.post(
        data["url"], 
        data=data["payload"], 
        headers=data["headers"]
    )
    cookie = TakionAPIDatadome.extract_cookie(res)

    session.cookies.set("datadome", cookie)
    print(f"Got cookie: {cookie[:15]}...{cookie[-15:]}")
    print("Loading page with cookie...")
    response = load_page(session, url)
    print(f"Got a response with status code {response.status_code} with the cookie")
    print(response.headers)