from comics.comicapi.genericmetadata import GenericMetadata
from comics.comicapi.issuestring import IssueString
from comics.comicapi.utils import listToString


def parseDateStr(date_str):
    day = None
    month = None
    year = None
    if date_str is not None:
        parts = date_str.split("-")
        year = parts[0]
        if len(parts) > 1:
            month = parts[1]
            if len(parts) > 2:
                day = parts[2]
        return day, month, year


def map_issue_resp_to_metadata(resp):
    metadata = GenericMetadata()

    metadata.series = resp["series"]
    metadata.volume = resp["volume"]

    num_s = IssueString(resp["number"]).asString()

    metadata.issue = num_s

    titles = resp["name"]
    title_list = []
    for title in titles:
        title_list.append(title)
    metadata.title = listToString(title_list)

    metadata.publisher = resp["publisher"]
    metadata.day, metadata.month, metadata.year = parseDateStr(resp["cover_date"])

    metadata.comments = resp["desc"]

    person_credits = resp["credits"]
    for person in person_credits:
        if "role" in person:
            roles = person["role"]
            for role in roles:
                metadata.addCredit(person["creator"], role["name"], False)

    story_arc_credits = resp["arcs"]
    arc_list = []
    for arc in story_arc_credits:
        arc_list.append(arc["name"])
    if len(arc_list) > 0:
        metadata.storyArc = listToString(arc_list)

    return metadata
