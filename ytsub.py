import sys
import json
import subprocess
from urllib.parse import urlparse, parse_qs
from os import (makedirs, path, listdir, remove)
from utils import (resolve_path, print_help, extract_info, zfilter)

DEFAULT_CONF = {
    "ytsub_dir": "~/.youtube-subscribe",
    "destination": "~/downloads",
    "options": {
        "output": "%(playlist)s/%(title)s.%(ext)s",
        "format": "best"
    }
}

CONF = {}
CONF.update(DEFAULT_CONF)

conf_path = "%s/conf.json" % path.dirname(path.realpath(__file__))

if not path.exists(conf_path):
    with open(conf_path, "w", encoding="utf-8") as fp:
        fp.write(json.dumps(CONF, ensure_ascii=False))

CONF.update(json.load(open(conf_path)))
CONF["ytsub_dir"] = resolve_path(CONF["ytsub_dir"])
makedirs(CONF["ytsub_dir"], exist_ok=True)


def call(verb, argv, **kwargs):
    getattr(sys.modules[__name__], "ytsub_%s" % verb)(*argv, **kwargs)


def ytsub_add(*args, overwrite=False, **kwargs):
    if not args or len(args) > 1:
        print_help(short=True)
        return

    pl_id = parse_arg_to_pl(args[0])["id"]
    (existed, pl) = load_pl(pl_id, create_new=True)

    if existed and not overwrite:
        print(r"Playlist{%s} has existed" % pl["title"])
        return

    if existed:
        print(r"Playlist{%s} will be overwritten" % pl["title"])

    pl = fetch_pl(pl["url"])
    save_pl(pl)
    print(r"Playlist{%s} is added" % pl["title"])


def ytsub_ls(*args, short=False, **kwargs):
    if len(args) > 1:
        print_help(short=True)
        return

    pls = load_pls()
    if not args:
        for pl in pls:
            print_pl(pl, short)
            if not short:
                print("\n")
    else:
        mstr = str(args[0])
        found = find_matching_pl(mstr)
        if not found:
            print("Can't match playlist by \"%s\"" % mstr)
        elif len(found) > 1:
            print("Found multiple matched playlists:")
            for pl in found:
                print("[%s] %s" % (pl["id"], pl["title"]))
        else:
            print_pl(found[0], short)


def ytsub_rm(*args, **kwargs):
    rm_all = kwargs.get("all", False)
    if not rm_all and len(args) != 1:
        print_help(short=True)
        return

    if rm_all:
        for pl in load_pls():
            remove(get_pl_path(pl["id"]))
            print(r"Playlist{%s} is removed" % pl["title"])
        return

    mstr = str(args[0])
    found = find_matching_pl(mstr)
    if not found:
        print("Can't match playlist by \"%s\"" % mstr)
    elif len(found) > 1:
        print("Found multiple matched playlists:")
        for pl in found:
            print("[%s] %s" % (pl["id"], pl["title"]))
    else:
        remove(get_pl_path(found[0]["id"]))


def ytsub_dl(*args, sync=False, **kwargs):
    if len(args) > 2:
        print_help(short=True)
        return

    if sync:
        found = find_matching_pl(args[0] if args else "")
        for pl in found:
            sync_pl(pl)

    found = find_matching_pl(args[0] if args else "")
    ep_indexes = parse_arg_to_ep_indexes(args[1] if len(args) > 1 else "")

    for pl in found:
        if not ep_indexes:
            # download all not downloaded
            for ep in zfilter(lambda ep: not ep["downloaded"], pl["eps"]):
                download_ep(pl, ep)
                print("%s is downloaded" % ep["filename"])
                save_pl(pl)
        else:
            # download ep by index
            for ep in zfilter(lambda ep: ep["index"] in ep_indexes, pl["eps"]):
                download_ep(pl, ep)
                print("%s is downloaded" % ep["filename"])
                save_pl(pl)


def parse_arg_to_pl(arg=""):
    _id = arg

    if arg.startswith("https://www.youtube.com/"):
        url = urlparse(arg)
        if url.path not in ["/playlist", "/watch"]:
            raise Exception("Bad <playlist>")

        qs_list = parse_qs(url.query).get("list")
        if qs_list:
            _id = qs_list[0]

    if _id.startswith("PL"):
        return {
            "id": _id,
            "url": "https://www.youtube.com/playlist?list=%s" % _id,
            "title": "",
            "eps": []
        }

    raise Exception("Bad <playlist>")


def parse_arg_to_ep_indexes(arg=""):
    a = arg.strip()
    if "," in a:
        eps = []
        for epstr in arg.split(","):
            eps.extend(parse_arg_to_ep_indexes(epstr))
        return list(set(eps))

    if "-" in arg:
        (s, t) = arg.split("-")
        return list(range(int(s.strip()), int(t.strip()) + 1))

    if a.isdecimal():
        return [int(a)]

    return []


def load_pl(pl_id, create_new=False):
    """
    return (exists, pl)

    pl = {
        id := str,
        url := str,
        title := str
        eps := list
    }
    """
    existed = True

    pl_path = get_pl_path(pl_id)

    if not path.exists(pl_path):
        existed = False
        pl = parse_arg_to_pl(pl_id)
        if not create_new:
            return (False, pl)

        save_pl(pl)

    return (existed, json.load(open(pl_path)))


def load_pls():
    pls = []
    for pl_path in listdir(CONF["ytsub_dir"]):
        (pl_id, ext) = path.splitext(pl_path)
        if ext == ".json":
            (_, pl) = load_pl(pl_id)
            pls.append(pl)
    return pls


def get_pl_path(pl_id):
    return resolve_path("%s/%s.json" % (CONF["ytsub_dir"], pl_id))


def fetch_pl(pl_url):
    pl = parse_arg_to_pl(pl_url)
    cmd = compose_pl_info_cmd(pl["url"])
    out = subprocess.run(cmd, capture_output=True, encoding="utf-8")

    infos = []
    for jsonstr in filter(bool, out.stdout.split("\n")):
        j = json.loads(jsonstr)
        info = extract_info(j)
        info["downloaded"] = False

        if not pl.get("title"):
            pl["title"] = info["playlist_title"]

        del info["playlist_title"]
        infos.append(info)

    pl["eps"] = sorted(infos, key=lambda x: x["index"])

    return pl


def compose_pl_info_cmd(pl_url):
    opt = CONF["options"]
    return [
        "youtube-dl", "--dump-json", "--output", opt["output"], "--format",
        opt["format"], pl_url
    ]


def save_pl(pl):
    with open(get_pl_path(pl["id"]), "w", encoding="utf-8") as fp:
        fp.write(json.dumps(pl, ensure_ascii=False))


def print_pl(pl, short=False):
    dd = len(zfilter(lambda ep: ep["downloaded"], pl["eps"]))

    if not short:
        print("playlist id: %s" % pl["id"])
        print("playlist title: %s" % pl["title"])
        print("----------")

        for ep in pl["eps"]:
            d = "o" if ep["downloaded"] else "x"
            i = "{:>2}".format(ep["index"])
            print("[%s] %s %s (%s)" % (i, d, ep["title"], ep["filename"]))

        print("==========")
        print("downloaded: %d, fetched: %d" % (dd, len(pl["eps"])))
    else:
        print("[%s] %s (%d/%d)" % (pl["id"], pl["title"], dd, len(pl["eps"])))


def find_matching_pl(mstr):
    return zfilter(lambda pl: mstr in pl["id"], load_pls())


def sync_pl(pl):
    """
    return sync_pl
    """
    local_pl = pl
    remote_pl = fetch_pl(pl["url"])

    def is_same_ep(rep):
        return lambda lep: lep["id"] == rep["id"]

    if len(remote_pl["eps"]) > len(local_pl["eps"]):
        for rep in remote_pl["eps"]:
            existed_eps_in_local = zfilter(is_same_ep(rep), local_pl["eps"])
            if not existed_eps_in_local:
                local_pl["eps"].append(rep)

        local_pl["eps"] = sorted(local_pl["eps"], key=lambda x: x["index"])
        save_pl(local_pl)

    return local_pl


def compose_dl_ep_cmd(pl, ep):
    final_output = "%s/%s" % (CONF["destination"], ep["filename"])

    return [
        "youtube-dl", "--output",
        resolve_path(final_output), "--format", CONF["options"]["format"],
        "https://www.youtube.com/watch?v=%s&list=%s" % (ep["id"], pl["id"])
    ]


def download_ep(pl, ep):
    cmd = compose_dl_ep_cmd(pl, ep)
    subprocess.run(cmd)
    ep["downloaded"] = True
