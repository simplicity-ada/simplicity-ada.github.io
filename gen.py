# -*- coding: utf-8 -*-
import json
import jinja2
from pathlib import Path
import re
from itertools import groupby

PWD = Path(__file__).absolute().parent

env = jinja2.Environment()


CAP_RE = re.compile("(.)([A-Z])")
LEADING_UNDERSCORE = re.compile("^(_*)")


def to_pascal_case(name):
    """
    Turn a snake_case name into PascalCase.
    """
    return name.title().replace("_", "")


def from_pascal_case(name):
    """
    Turn a PascalCase name into snake_case.
    """
    return CAP_RE.sub(r"\1_\2", name).lower()


def to_camel_case(name):
    """
    Turn a snake_case name into camelCase.
    """
    mat = LEADING_UNDERSCORE.match(name)
    leading_underscores = mat.group()

    output = name[len(leading_underscores) :].title().replace("_", "")
    return output


def to_kebab_case(name):
    """
    Turn a snake_case name into kebab-case
    """
    return name.replace("_", "-")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def process(policy_id: str, token: str, nft: dict) -> dict:
    ipfs = nft["image"].split("://")[1]
    nft["policy_id"] = policy_id
    nft["token"] = token
    nft["url"] = f"./nft/{to_kebab_case(from_pascal_case(token))}.png"
    nft["ipfs"] = ipfs
    nft["pool_pm"] = f"https://pool.pm/{policy_id}.{token}"
    # nft["ipfs_url"] = f"https://ipfs.io/ipfs/{ipfs}"
    nft["ipfs_url"] = f"https://cloudflare-ipfs.com/ipfs/{ipfs}"
    return nft


def add_scarcity(nft: dict, total: int) -> dict:
    nft["scarcity"] = int(nft["distribution"]) / total
    nft["scarcity_percentage"] = f"{nft['scarcity'] * 100 :.2f}%"
    return nft


def main():
    with open(PWD / "templates" / "nft.jinja") as t:
        template = env.from_string(t.read())

    metadata = json.load(open(PWD / "nft" / "block-dragon.json"))
    policy_id = list(list(metadata.values())[0].keys())[0]
    nfts = [
        process(policy_id, token, nft)
        for token, nft in list(list(metadata.values())[0].values())[0].items()
    ]
    total = sum([int(nft["distribution"]) for nft in nfts])
    nfts = [add_scarcity(nft, total) for nft in nfts]
    nfts = sorted(nfts, key=lambda nft: int(nft["distribution"]))
    groups = [
        list(group)
        for key, group in groupby(nfts, key=lambda nft: int(nft["distribution"]))
    ]
    result = template.render(groups=groups)
    with open(PWD / "index.html", "w") as f:
        f.write(result)


if __name__ == "__main__":
    main()
