import os

import json


def save(DATA, TARGET, override, pretty=False):
    if not os.path.isfile(TARGET) or override:
        with open(TARGET, "wb") as trg:
            if pretty:
                compressed = (json.dumps(DATA, ensure_ascii=False, sort_keys=False, indent=3, separators=(',', ': ')))
            else:
                compressed = (json.dumps(DATA, ensure_ascii=False, sort_keys=False, indent=None, separators=None))

            trg.write(compressed.encode("utf-8"))

        return True

    return False


def load(TARGET):
    if os.path.isfile(TARGET):
        with open(TARGET, encoding="utf-8") as entrada:
            return json.load(entrada)

    return None