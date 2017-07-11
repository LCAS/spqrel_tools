def lines_to_list(_file):
    with open(_file) as f:
        _list = f.readlines()
    return [x.strip() for x in _list]


def normalize(sublist):
    m = .0
    for trans in sublist:
        m = m + sublist[trans]
    for trans in sublist:
        sublist[trans] = sublist[trans] / m
    return sublist


def list_to_dict(transcriptions):
    d = {}
    for asr in transcriptions:
        counter = 0
        d[asr[0]] = {}
        for trans in asr[1]:
            counter = counter + 1
            d[asr[0]][trans] = counter
    return d


def list_to_dict_w_probabilities(transcriptions):
    d = {}
    for asr in transcriptions:
        d[asr[0]] = {}
        for trans in asr[1]:
            d[asr[0]][trans[0]] = trans[1]
    return d


def pick_best(transcriptions):
    confidence = 1.1
    for asr in transcriptions:
        for hypo in transcriptions[asr]:
            if transcriptions[asr][hypo] < confidence:
                best_hypo = hypo
                confidence = transcriptions[asr][hypo]
    return best_hypo
