# takion-api
This is the official repository for the TakionAPI Python library. TakionAPI is a non-browser-based automation solution focused antibot and captchas systems.

![TakionAPI](https://takionapi.tech/banner)

## Table of Contents
- [takion-api](#takion-api)
  - [Table of Contents](#table-of-contents)
  - [Revolutionizing Antibot Interactions](#revolutionizing-antibot-interactions)
  - [Get Your Free Trial API Key](#get-your-free-trial-api-key)
  - [Installation](#installation)
  - [Future Extensions](#future-extensions)
  - [Antibots](#antibots)
    - [Datadome](#datadome)
      - [Datadome challenges](#datadome-challenges)
        - [Geetest - Slide captcha](#geetest---slide-captcha)
        - [Interstitial - Device check](#interstitial---device-check)
      - [Usage](#usage)
      - [Exceptions](#exceptions)
  - [Support and Links](#support-and-links)

## Revolutionizing Antibot Interactions
TakionAPI stands at the forefront of antibot solutions, offering a robust and efficient way to bypass advanced bot protection systems like Datadome. Renowned for its non-browser-based approach, it ensures high-speed, accurate automation across various browser OS/versions. TakionAPI is committed to providing 24/7 uninterrupted service, adapting swiftly to changes in antibot technologies.

Key Features:
- **Non-Browser Automation:** For faster, error-free interactions.
- **Universal Browser Support:** Compatible with all browser OS/versions.
- **Continuous Service:** Round-the-clock availability and updates.
- **Free Trials & Comprehensive Plans:** Accessible, cost-effective solutions for every need.
- **Easy Integration:** Complete with documentation, libraries, and examples.
- **Dedicated Server Options:** Tailored solutions for specific requirements.
- **Community & Support:** Active Discord community and responsive support.

[Explore More](https://docs.takionapi.tech)

## Get Your Free Trial API Key
Start with a free trial by visiting [TakionAPI.tech](https://takionapi.tech). Join the [Discord community](https://takionapi.tech/discord) to acquire a trial key or subscription.

## Installation
Install the library using pip:
```bash
pip install takion-api
```

## Future Extensions
The current implementation of the takion-api module focuses on making the interactions with Datadome websites easier using out APIs.

However, we already support several bot protections solved with our APIs, are planning to extend this module to handle all the supported antibots.

For now you can interact with them using our [API](https://docs.takionapi.tech) directly.

## Antibots 

### Datadome
Datadome is a bot management system that protects websites from automated threats, including scraping, credential stuffing, and layer 7 (application layer) DDoS attacks. 

It's known for its inefficiency in detecting and blocking bots, resulting in false positives and IP bans for legitimate users.

Datadome is particularly sensitive to TLS fingerprinting and headers order, making it crucial to emulate a genuine browser's TLS signatures and headers sequence for successful bypass. 

Therefore, it's advisable to have a robust proxy list to rotate IPs and avoid IP bans.

[Learn More](https://docs.takionapi.tech/datadome/docs)

#### Datadome challenges
In order to access a Datadome website under protection you may need on first join or after some requests to solve a challenge that will generate you a `datadome` cookie that will garant you the access to the website for a certain amount of time.

##### Geetest - Slide captcha
This is a slide captcha that requires the user to slide a puzzle piece to a target location.
![SlideCaptcha](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2Fn0x4RrnIfxXvmfh6rJHh%2Fuploads%2F7oP27wbOKRLmDaDsLEhw%2FScreenshot%202023-12-12%20at%2014.43.11.png?alt=media&token=93b4ff62-c1b4-4023-bb70-0dc70177e56c)

##### Interstitial - Device check
This is the newest challenge, that similar to the Cloudflare 5s page, is going to make some checks on the browser.
![DeviceCheck](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2Fn0x4RrnIfxXvmfh6rJHh%2Fuploads%2FDBJewaVe0AhrMLYEaSgJ%2FScreenshot%202023-12-12%20at%2014.38.16.png?alt=media&token=0483815e-f2c6-48ec-96d3-27cd30bff5d3)


#### Usage
```python
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
        api_key="TAKION_API_XXXXXX", # Your TakionAPI key
    )
    session = Session(
        "chrome_110", 
        header_order=[ # The order of the headers is important
            'Host', 'Connection', 'Content-Length', 
            'sec-ch-ua', 'sec-ch-ua-platform', 
            'sec-ch-ua-mobile', 'User-Agent', 
            'Content-Type', 'Accept', 'Origin', 
            'Sec-Fetch-Site', 'Sec-Fetch-Mode', 
            'Sec-Fetch-Dest', 'Referer', 'Accept-Encoding', 
            'Accept-Language'
        ]
    )

    # An example Datadome protected page
    url = "https://www.footlocker.pt/en/product/~/314206535404.html"
    
    response = load_page(session, url)
    if not takion_api.is_challenge(response): # Check if we need to solve a challenge
        print("Page loaded successfully")
        exit(0)
    
    print(f"Got a response with status code {response.status_code} without the cookie")

    # This function will return the url of the challenge
    # no matter if it's a slide captcha or an interstital
    challenge_url = takion_api.get_challenge_url(
        url,
        response,
        session.cookies.get_dict().get("datadome")
    )
    print(f"Solving {takion_api.challenge_type} challenge...")

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
    
    # After that we are going to load the challenge page
    response = session.get(challenge_url, headers=headers)

    # And send to TakionAPI the content, in order to solve any present challenge
    data = takion_api.solve_challenge(
        response
    )

    # TakionAPI will return a dict with the url, payload and headers
    # for the POST request that we need to send to the challenge page
    # in order to generate the cookie
    res = session.post(
        data["url"], 
        data=data["payload"], 
        headers=data["headers"]
    )

    # We extract the cookie from the response
    cookie = TakionAPIDatadome.extract_cookie(res)

    # And set it in the session
    session.cookies.set("datadome", cookie)
    print(f"Got cookie: {cookie[:15]}...{cookie[-15:]}")

    # Now we can load the page with the cookie
    print("Loading page with cookie...")
    response = load_page(session, url)
    print(f"Got a response with status code {response.status_code} with the cookie")
```

#### Exceptions
- `TakionAPIException`: Generic exception
- `BadResponseException`: Raised when the response is not a valid response, error solving or wrong parameters provided
- `IpBanException`: Raised when the IP is banned

## Support and Links
- [TakionAPI.tech](https://takionapi.tech)
- [Documentation](https://docs.takionapi.tech)
- [Discord / Start a trial](https://takionapi.tech/discord)
- [Buy a plan](https://takionapi.tech/buy)
- [GitHub](https://github.com/Takion-API-Services)

For any question or issue, please contact us on [Discord](https://takionapi.tech/discord).

----

TakionAPI is a product of [Takion Labs](https://takionapi.com/), a leading provider of automation solutions for businesses and individuals.