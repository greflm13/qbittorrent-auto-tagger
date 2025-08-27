import re
import os
import yaml
import argparse

import qbittorrentapi


if "APPDATA" in os.environ:
    CONFIGHOME = os.environ["APPDATA"]
elif "XDG_CONFIG_HOME" in os.environ:
    CONFIGHOME = os.environ["XDG_CONFIG_HOME"]
else:
    CONFIGHOME = os.path.join(os.environ["HOME"], ".config")
CONFIGPATH = os.path.join(CONFIGHOME, "qbittorrent-auto-tagger")
KNOWNTORRENTS = os.path.join(CONFIGPATH, "known-torrents")
CONFIGFILE = os.path.join(CONFIGPATH, "tags.yml")
if not os.path.exists(CONFIGPATH):
    if not os.path.exists(CONFIGHOME):
        os.makedirs(CONFIGHOME)
    os.makedirs(CONFIGPATH)
if not os.path.exists(KNOWNTORRENTS):
    open(KNOWNTORRENTS, "x", encoding="utf-8")
if not os.path.exists(CONFIGFILE):
    with open(CONFIGFILE, "w+", encoding="utf-8") as f:
        empty = {"case_sensitive": [], "case_insensitive": [], "regex": []}
        yaml.dump(empty, f)


def argpar():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--host", help="qbittorrent url", required=True, type=str, dest="host")
    parser.add_argument("-o", "--port", help="qbittorrent port", required=False, type=int, dest="port", default=443)
    parser.add_argument("-u", "--user", help="qbittorrent user", required=True, type=str, dest="user")
    parser.add_argument("-p", "--password", help="qbittorrent password", required=True, type=str, dest="passw")
    parser.add_argument("--tag-new", help="add a tag to all new torrents", required=False, action="store_true", dest="tagnew")
    return parser.parse_args()


def main():
    args = argpar()
    knowntorrents = []

    with open(CONFIGFILE, mode="r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.tagnew:
        with open(KNOWNTORRENTS, "r", encoding="utf-8") as f:
            knowntorrents = [name.removesuffix(os.linesep) for name in f.readlines()]

    client = qbittorrentapi.Client(host=args.host, port=args.port, username=args.user, password=args.passw, VERIFY_WEBUI_CERTIFICATE=False)
    client.auth_log_in()

    torrentlist = client.torrents.info(sort="added_on")

    for torrent in torrentlist:
        name = str(torrent["name"])
        tags = [tag.strip() for tag in str(torrent["tags"]).split(",")]
        newtags = []
        for pattern in config["case_sensitive"]:
            if pattern in name:
                if pattern not in tags:
                    newtags.append(pattern)
        for pattern in config["case_insensitive"]:
            if pattern.lower() in name.lower():
                if pattern not in tags:
                    newtags.append(pattern)
        for pattern in config["regex"]:
            if re.search(pattern["pattern"], name.lower()):
                if pattern["tag"] not in tags:
                    newtags.append(pattern["tag"])
        if args.tagnew:
            if name not in knowntorrents:
                newtags.append("new")
                knowntorrents.append(name)
        if len(newtags) > 0:
            print(f"adding tags to {name}: {', '.join(set(newtags))}")
            torrent.add_tags(set(newtags))

    client.auth_log_out()

    if args.tagnew:
        with open(KNOWNTORRENTS, "w", encoding="utf-8") as f:
            for name in knowntorrents:
                f.write(name + os.linesep)


if __name__ == "__main__":
    main()
