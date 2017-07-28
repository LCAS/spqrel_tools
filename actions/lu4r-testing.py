import requests
import qi
import execplan
import action_base

from json import loads, dumps

LU4R_URI = 'http://192.168.127.16:9001/service/nlu'

if __name__ == "__main__":
    app = action_base.initApp('lu4rtest')
    memory_service = app.session.service("ALMemory")


def load_text(filename="utterances.txt"):
    with open(filename) as f:
        data = f.read()
        return data.split('\n')


def ask_lu4r(utterance):
    lu4r_input = {
        'hypotheses': [
            {
                'transcription': utterance,
                'confidence': 1.0,
                'rank': 1
            }
        ]
    }
    return loads(
        requests.post(LU4R_URI, data=dumps(lu4r_input))
    )


def to_plan(frame):
    return execplan.LU4R_to_plan(frame, memory_service)


if __name__ == "__main__":
    utterances = load_text()
    for u in utterances:
        if '#' not in u:
            print 'testing utterance: %s' % u
            frame = ask_lu4r(u)
            print 'ok'
            print to_plan(frame)
