import re


def parse_msg(msg):
    if msg.endswith("\u0000"):
        msg = msg[:-len("\u0000")]

    tokens = re.findall(r'(\(|[-\d\.]+|[\\\"\w]+|\))', msg)

    result = {'msg': msg, 'p': []}
    parse(tokens, {"idx": 0}, result)
    make_cmd(result)
    return result


def parse(tokens, index, res):
    if tokens[index["idx"]] != '(':
        return
    index["idx"] += 1
    parse_inner(tokens, index, res)


def parse_inner(tokens, index, res):
    while tokens[index["idx"]] != ')':
        if tokens[index["idx"]] == '(':
            nested = {'p': []}
            parse(tokens, index, nested)
            res['p'].append(nested)
        else:
            token = tokens[index["idx"]]
            res['p'].append(token)
            index["idx"] += 1
    index["idx"] += 1


def make_cmd(res):
    if 'p' in res and res['p']:
        first = res['p'].pop(0)
        res['cmd'] = first
        for item in res['p']:
            if isinstance(item, dict) and 'p' in item:
                make_cmd(item)
