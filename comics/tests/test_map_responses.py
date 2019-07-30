from comics.utils.mapresponse import map_issue_resp_to_metadata

from django.test import TestCase


class TestMapResponses(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.issue = {
            "id": 479,
            "publisher": "DC Comics",
            "series": "Action Comics",
            "volume": 3,
            "number": "957",
            "name": ["Path of Doom Part One"],
            "cover_date": "2016-08-01",
            "store_date": "2016-06-08",
            "desc": "Superman returns to Metropolis just in time to meet the city of tomorrow’s newest protector: Lex Luthor. But it’s not long before these dueling titans meet someone unexpected — the new Clark Kent!\r\n\r\nDON’T MISS: ACTION COMICS returns to its original numbering with this issue!",
            "image": "https://static.metron.cloud/media/issue/2018/12/17/action-957.jpg",
            "arcs": [{"id": 28, "name": "Path of Doom"}],
            "credits": [
                {
                    "id": 26,
                    "creator": "Dan Jurgens",
                    "role": [{"id": 1, "name": "Writer"}],
                },
                {
                    "id": 739,
                    "creator": "Eddie Berganza",
                    "role": [{"id": 11, "name": "Group Editor"}],
                },
                {
                    "id": 54,
                    "creator": "Ivan Reis",
                    "role": [{"id": 7, "name": "Cover"}],
                },
                {
                    "id": 58,
                    "creator": "Joe Prado",
                    "role": [{"id": 7, "name": "Cover"}],
                },
                {
                    "id": 191,
                    "creator": "Mike Cotton",
                    "role": [{"id": 8, "name": "Editor"}],
                },
                {
                    "id": 248,
                    "creator": "Patrick Zircher",
                    "role": [{"id": 2, "name": "Artist"}],
                },
                {
                    "id": 61,
                    "creator": "Paul Kaminski",
                    "role": [{"id": 9, "name": "Associate Editor"}],
                },
                {
                    "id": 107,
                    "creator": "Rob Leigh",
                    "role": [{"id": 6, "name": "Letterer"}],
                },
                {
                    "id": 24,
                    "creator": "Ryan Sook",
                    "role": [{"id": 7, "name": "Cover"}],
                },
                {
                    "id": 807,
                    "creator": "Sonia Oback",
                    "role": [{"id": 7, "name": "Cover"}],
                },
                {
                    "id": 449,
                    "creator": "Tomeu Morey",
                    "role": [{"id": 5, "name": "Colorist"}],
                },
            ],
            "characters": [
                {"id": 860, "name": "Doomsday"},
                {"id": 102, "name": "Jimmy Olsen"},
                {"id": 99, "name": "Jon Kent"},
                {"id": 191, "name": "Lex Luthor"},
                {"id": 20, "name": "Lois Lane"},
                {"id": 851, "name": "Maggie Sawyer"},
                {"id": 13, "name": "Superman"},
            ],
            "teams": [],
        }

    def test_map_issue_response(self):
        md = map_issue_resp_to_metadata(self.issue)
        self.assertIsNotNone(md)
        self.assertEqual(md.publisher, self.issue["publisher"])
        self.assertEqual(md.series, self.issue["series"])
        self.assertEqual(md.issue, self.issue["number"])

