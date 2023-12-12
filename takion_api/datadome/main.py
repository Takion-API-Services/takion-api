from requests import post
from requests.models import Response
from typing import Optional, Dict, TypedDict

from .exceptions import BadResponseException, IpBanException

class CookieRequest(TypedDict):
    payload: Dict[str, str]
    headers: Dict[str, str]
    url: str

class TakionAPIDatadome:
    BASE_URL = "https://takionapi.tech/datadome/{}?api_key={}"
    api_key: str
    challenge_type: Optional[str]

    @staticmethod
    def is_challenge(response: Response) -> bool:
        """
        # Got Flagged by Datadome?
        ## Check if the response is a Datadome challenge
        This is a very basic check, it only checks if the server is Datadome protected,
        response status code is 403 or the page contains the Datadome domains.
        This method should be edited based on the website you are trying to access.

        ### Parameters
        - `response`: The response object to check

        ### Returns
        - `bool`: True if the response is a Datadome challenge, False otherwise
        """
        if not response.headers.get("Server") == "DataDome":
            # Server is not Datadome protected
            return False
        if response.status_code == 403:
            # Server is Datadome protected 
            # and we has been blocked
            return True
        # Check if the page contains the Datadome domains
        return "geo.captcha-delivery.com" in response.text or \
            "interstitial.captcha-delivery.com" in response.text

    @staticmethod
    def extract_cookie(response: Response) -> str:
        '''
        ## Extract Cookie
        Extract the Datadome cookie from the response headers
        
        ### Parameters 
        - `response`: The response object to extract the cookie from
        
        ### Returns
        - `str`: The Datadome cookie
        
        ### Raises
        - `BadResponseException`: If the cookie could not be extracted from the response
        '''
        try:
            return response.json()["cookie"].split(";")[0].split("=")[1]
        except:
            raise BadResponseException("Could not extract cookie from response")

    def __init__(
        self,
        api_key: str,
    ) -> None:
        '''
        # Takion API
        ## Datadome API wrapper for Takion
        This class is a wrapper for the Datadome API, it can be used to solve Datadome challenges.
        To get your takion API key please check the [Takion API](https://takionapi.tech/) website.

        ### Parameters
        - `api_key`: The API key to use

        ### Example Usage
        ```py
        from requests import Session
        from takion_api import TakionAPIDatadome

        session = Session()
        takion_api = TakionAPIDatadome(
            api_key="TAKION_API_XXXXXXXXXX"
        )
        url = "https://www.footlocker.pt/en/product/~/314206535404.html"
        headers = {...}
        response = session.get(url, headers=headers)
        if not takion_api.is_challenge(response):
            print("Page loaded successfully")
        else:
            print("Solving challenge...")
            # Load the challenge url
            challenge_url = takion_api.get_challenge_url(
                url,
                response,
                session.cookies.get_dict().get("datadome")
            )
            # Load the challenge page
            challenge_response = session.get(challenge_url, headers=headers)
            # Solve the challenge
            data = takion_api.solve_challenge(
                challenge_response
            )
            # Send the cookie generation request
            cookie_response = session.post(
                data["url"], 
                data=data["payload"], 
                headers=data["headers"]
            )
            cookie = TakionAPIDatadome.extract_cookie(cookie_response)
            session.cookies.set("datadome", cookie)
            print(f"Got cookie: {cookie[:15]}...{cookie[-15:]}")
            # Now we send the original request again
            response = session.get(url, headers=headers)
            print(f"Got a response with status code {response.status_code} with the cookie")
        '''
        self.api_key = api_key
        self.challenge_type = None
        pass

    def get_challenge_url(
        self,
        url: str,
        response: Response,
        cookie: str,
        user_agent: Optional[str]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ) -> str:
        '''
        # Parse, build and return the challenge URL
        
        ### Parameters
        - `url`: The URL of the page that returned the challenge
        - `response`: The response of the challenge page (the page returned by get_challenge_url)
        - `cookie`: The Datadome cookie setted on the previous request
        - `user_agent`: The User-Agent used to request the challenge page

        ### Returns
        - `str`: The challenge URL

        ### Raises
        - `BadResponseException`: If the challenge URL could not be parsed from the response
        '''
        try:
            res = post(
                self.BASE_URL.format(
                    "build-url",
                    self.api_key,
                ),
                json={
                    "html": response.text,
                    "cid": cookie,
                    "referrer": url,
                },
                headers={
                    "User-Agent": user_agent,
                },
            ).json()
        except:
            raise BadResponseException("Could not parse challenge URL from response")
        if not (url := res.get("url")):
            raise BadResponseException(res.get('error'))
        self.challenge_type = res.get("challenge_type")
        return url
    
    def solve_challenge(
        self,
        response: Response,
        user_agent: Optional[str]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        challenge_type: Optional[str]=None,
    ) -> Dict[str, CookieRequest]:
        '''
        # Solve the challenge
        Solve the challenge and return the payload, headers and url for the cookie generation request

        ### Parameters
        - `response`: The response of the challenge page (the page returned by get_challenge_url)
        - `user_agent`: The User-Agent used to request the challenge page
        - `challenge_type`: The challenge type to use (optional, can be `interstitial` or `geetest`)

        ### Returns
        - `Dict[str, CookieRequest]`: The payload, headers and url for the cookie generation request

        ### Raises
        - `BadResponseException`: If the challenge could not be solved
        - `ValueError`: If the challenge type is not set and the challenge_type parameter is not set
        - `IpBanException`: If the IP is banned

        ### Notes
        - The challenge type is automatically set by the get_challenge_url method
        - The challenge type can be forced by the challenge_type parameter
        '''
        if not self.challenge_type and challenge_type not in ["interstitial", "geetest"]:
            raise ValueError("Challenge type not set")
        elif not self.challenge_type and challenge_type in ["interstitial", "geetest"]:
            self.challenge_type = challenge_type
        
        try:
            res = post(
                self.BASE_URL.format(
                    self.challenge_type,
                    self.api_key,
                ),
                json={
                    "html": response.text,
                },
                headers={
                    "User-Agent": user_agent,
                }
            ).json()
        except:
            raise BadResponseException("Could not solve challenge")
        if (error := res.get("error")):
            if error == 'Ip banned': raise IpBanException(error)
            raise BadResponseException(error)
        return res