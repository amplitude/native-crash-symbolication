import json
import datetime
from date import isoformat

class BetterJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date) or \
           isinstance(o, datetime.datetime):
            return isoformat(o)
        else:
            return json.JSONEncoder.default(self, o)

def dumps(o):
    string = json.dumps(o, cls=BetterJSONEncoder)
    return string

def loads(string):
    return json.loads(string)
