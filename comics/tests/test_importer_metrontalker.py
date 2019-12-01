from base64 import standard_b64encode
from unittest import TestCase
from unittest.mock import patch

from comics.importer.metrontalker import MetronTalker


class TestMetronTalker(TestCase):
    def setUp(self):
        auth = f"test_user:test_auth"
        self.base64string = standard_b64encode(auth.encode("utf-8"))
        self.talker = MetronTalker(self.base64string)
        self.arc = {
            "id": 1,
            "name": "Heroes In Crisis",
            "desc": "Heroes in Crisis is a nine issue series that deals with the emotional cost of being a superhero.",
            "image": "https://static.metron.cloud/media/arc/2018/11/12/heroes-in-crisis.jpeg",
        }
        self.publisher = {
            "id": 1,
            "name": "Marvel",
            "founded": 1939,
            "desc": "Marvel Comics is the brand name and primary imprint of Marvel Worldwide Inc.",
            "image": "https://static.metron.cloud/media/publisher/2018/11/11/marvel.jpg",
        }
        self.series = {
            "id": 1,
            "name": "Death of the Inhumans",
            "sort_name": "Death of the Inhumans",
            "volume": 1,
            "series_type": {"id": 3, "name": "Mini-Series"},
            "publisher": 1,
            "year_began": 2018,
            "year_end": 2018,
            "desc": "The alien Kree are on a killing spree, leaving behind a message: Join or die.",
            "issue_count": 5,
            "image": "https://static.metron.cloud/media/issue/2018/11/11/6497376-01.jpg",
        }
        self.creator = {
            "id": 322,
            "name": "Chuck Dixon",
            "birth": "1954-04-14",
            "death": None,
            "desc": "Charles Dixon is an American comic book writer",
            "image": "https://static.metron.cloud/media/creator/2018/11/18/chuck-dixon.jpg",
        }
        self.issue = {
            "id": 2471,
            "publisher": "DC Comics",
            "series": "Aquaman",
            "volume": "2",
            "number": "1",
            "name": [],
            "cover_date": "1986-02-01",
            "store_date": None,
            "desc": "Aquaman settles back in New Venice",
            "image": "https://metron.cloud/media/issue/2019/05/19/aquaman-v2-1.jpg",
            "arcs": [],
            "credits": [
                {
                    "id": 1566,
                    "creator": "Bob Lappan",
                    "role": [{"id": 6, "name": "Letterer"}],
                },
                {
                    "id": 1614,
                    "creator": "Craig Hamilton",
                    "role": [{"id": 2, "name": "Artist"}, {"id": 7, "name": "Cover"}],
                },
                {
                    "id": 399,
                    "creator": "Dick Giordano",
                    "role": [{"id": 8, "name": "Editor"}],
                },
                {
                    "id": 1977,
                    "creator": "Joe Orlando",
                    "role": [{"id": 5, "name": "Colorist"}],
                },
                {
                    "id": 1975,
                    "creator": "Neal Pozner",
                    "role": [{"id": 30, "name": "Story"}, {"id": 8, "name": "Editor"}],
                },
                {
                    "id": 1976,
                    "creator": "Steve Montano",
                    "role": [{"id": 4, "name": "Inker"}],
                },
            ],
            "characters": [
                {"id": 86, "name": "Aquaman"},
                {"id": 530, "name": "Mera"},
                {"id": 1773, "name": "Nuada Silver-Hand"},
                {"id": 1520, "name": "Ocean Master"},
                {"id": 1500, "name": "Vulko"},
            ],
            "teams": [],
        }

    @patch("comics.importer.metrontalker.MetronTalker.fetch_response")
    def test_fetch_issue_by_id(self, mock_fetch):
        mock_fetch.return_value = self.issue
        talker = MetronTalker(self.base64string)
        resp = talker.fetch_issue_data("1")
        self.assertIsNotNone(resp)
        self.assertEqual(resp["series"], self.issue["series"])
        self.assertEqual(resp["number"], self.issue["number"])

    @patch("comics.importer.metrontalker.MetronTalker.fetch_response")
    def test_fetch_creator_by_id(self, mock_fetch):
        mock_fetch.return_value = self.creator
        talker = MetronTalker(self.base64string)
        resp = talker.fetch_creator_data("322")
        self.assertIsNotNone(resp)
        self.assertEqual(resp["name"], self.creator["name"])

    @patch("comics.importer.metrontalker.MetronTalker.fetch_response")
    def test_fetch_series_by_id(self, mock_fetch):
        mock_fetch.return_value = self.series
        talker = MetronTalker(self.base64string)
        resp = talker.fetch_series_data("1")
        self.assertIsNotNone(resp)
        self.assertEqual(resp["name"], self.series["name"])
        self.assertEqual(resp["volume"], self.series["volume"])
        self.assertEqual(resp["publisher"], self.series["publisher"])
        self.assertEqual(resp["series_type"]["id"], self.series["series_type"]["id"])

    @patch("comics.importer.metrontalker.MetronTalker.fetch_response")
    def test_fetch_publisher_by_id(self, mock_fetch):
        mock_fetch.return_value = self.publisher
        talker = MetronTalker(self.base64string)
        resp = talker.fetch_publisher_data("1")
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], self.publisher["id"])
        self.assertEqual(resp["name"], self.publisher["name"])
        self.assertEqual(resp["founded"], self.publisher["founded"])

    @patch("comics.importer.metrontalker.MetronTalker.fetch_response")
    def test_fetch_arc_by_id(self, mock_fetch):
        mock_fetch.return_value = self.arc
        talker = MetronTalker(self.base64string)
        resp = talker.fetch_arc_data("1")
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], self.arc["id"])
        self.assertEqual(resp["name"], self.arc["name"])
        self.assertEqual(resp["desc"], self.arc["desc"])
