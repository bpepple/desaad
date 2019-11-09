import json
import platform
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ratelimit import limits, sleep_and_retry

ONE_MINUTE = 60


class MetronTalker:
    def __init__(self, auth):
        self.baseurl = "https://metron.cloud/api"
        self.auth_str = f"Basic {auth.decode('utf-8')}"
        self.user_agent = f"desaad/version ({platform.system()}; {platform.release()})"

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
        except HTTPError as h_error:
            # TODO: Look into handling throttling better, but for now let's use this.
            if h_error.code == 429:
                print("Exceeded api rate limit. Sleeping for 30 seconds...")
                time.sleep(30)
                return self.fetch_response(url)
            raise

        resp = json.loads(content.read().decode("utf-8"))

        return resp

    @staticmethod
    def fetch_image(url, file_name):
        with urlopen(url) as img:
            with open(file_name, "wb") as m_image:
                m_image.write(img.read())

    def fetch_publisher_data(self, m_id):
        url = self.baseurl + f"/publisher/{m_id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_series_data(self, m_id):
        url = self.baseurl + f"/series/{m_id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_arc_data(self, m_id):
        url = self.baseurl + f"/arc/{m_id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_issue_data(self, m_id):
        url = self.baseurl + f"/issue/{m_id}/?format=json"
        resp = self.fetch_response(url)
        return resp

    def fetch_creator_data(self, m_id):
        url = self.baseurl + f"/creator/{m_id}/?format=json"
        resp = self.fetch_response(url)
        return resp
