"""A python class to manage communication with Metron's REST API"""
import json
import platform
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import logging

from ratelimit import limits, sleep_and_retry

ONE_MINUTE = 60


class MetronTalker:
    """Python class to communicate with Metron's REST API"""

    def __init__(self, auth):
        self.logger = logging.getLogger(__name__)
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
                self.logger.warning("Exceeded api rate limit. Sleeping for 30 seconds...")
                time.sleep(30)
                return self.fetch_response(url)
            raise

        return json.loads(content.read().decode("utf-8"))

    def fetch_image(self, url, file_name):
        try:
            with urlopen(url) as img:
                with open(file_name, "wb") as m_image:
                    m_image.write(img.read())
        except HTTPError as h_error:
            if h_error.code == 504:
                self.logger.warning("Gateway Timeout. Sleeping for 60 seconds...")
                time.sleep(ONE_MINUTE)
                return self.fetch_image(url, file_name)
            raise

    def fetch_publisher_data(self, m_id):
        url = self.baseurl + f"/publisher/{m_id}/?format=json"
        return self.fetch_response(url)

    def fetch_series_data(self, m_id):
        url = self.baseurl + f"/series/{m_id}/?format=json"
        return self.fetch_response(url)

    def fetch_arc_data(self, m_id):
        url = self.baseurl + f"/arc/{m_id}/?format=json"
        return self.fetch_response(url)

    def fetch_issue_data(self, m_id):
        url = self.baseurl + f"/issue/{m_id}/?format=json"
        return self.fetch_response(url)

    def fetch_creator_data(self, m_id):
        url = self.baseurl + f"/creator/{m_id}/?format=json"
        return self.fetch_response(url)

    def fetch_character_data(self, m_id):
        url = self.baseurl + f"/character/{m_id}/?format=json"
        return self.fetch_response(url)

    def fetch_team_data(self, m_id):
        url = self.baseurl + f"/team/{m_id}/?format=json"
        return self.fetch_response(url)
