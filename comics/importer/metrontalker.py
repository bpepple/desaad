import json
import platform
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ratelimit import limits, sleep_and_retry

ONE_MINUTE = 60


class MetronTalker:
    def __init__(self, auth):
        self.baseurl = "https://metron.cloud/api"
        self.auth_str = f"Basic {auth.decode('utf-8')}"
        self.user_agent = (
            f"desaad/version ({platform.system()}; {platform.release()})"
        )

    @sleep_and_retry
    @limits(calls=20, period=ONE_MINUTE)
    def fetch_response(self, url):
        if url.lower().startswith("https"):
            request = Request(url)
        else:
            raise ValueError from None
        
        request.add_header("Authorization", self.auth_str)
        request.add_header("User-Agent", self.user_agent)

        try:
            content = urlopen(request)
        except HTTPError as e:
            # TODO: Look into handling throttling better, but for now let's use this.
            if e.code == 429:
                print("Exceeded api rate limit. Sleeping for 30 seconds...")
                time.sleep(30)
                return self.fetchResponse(url)
            raise

        resp = json.loads(content.read().decode("utf-8"))

        return resp

    def fetch_publisher_data(self, id):
        url = self.baseurl + f"/publisher/{id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_series_data(self, id):
        url = self.baseurl + f"/series/{id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_arc_data(self, id):
        url = self.baseurl + f"/arc/{id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_issue_data(self, id):
        url = self.baseurl + f"/issue/{id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_creator_data(self, id):
        url = self.baseurl + f"/creator/{id}/?format=json"
        resp = self.fetch_response(url)
        return resp