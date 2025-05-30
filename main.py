import re
import os
import argparse

import qbittorrentapi


if "APPDATA" in os.environ:
    confighome = os.environ["APPDATA"]
elif "XDG_CONFIG_HOME" in os.environ:
    confighome = os.environ["XDG_CONFIG_HOME"]
else:
    confighome = os.path.join(os.environ["HOME"], ".config")
configpath = os.path.join(confighome, "qbittorrent-auto-tagger")
if not os.path.exists(configpath):
    if not os.path.exists(confighome):
        os.makedirs(confighome)
    open(configpath, "x", encoding="utf-8")


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

    if args.tagnew:
        with open(configpath, "r", encoding="utf-8") as f:
            knowntorrents = [name.removesuffix(os.linesep) for name in f.readlines()]

    client = qbittorrentapi.Client(host=args.host, port=args.port, username=args.user, password=args.passw, VERIFY_WEBUI_CERTIFICATE=False)
    client.auth_log_in()

    torrentlist = client.torrents.info(sort="added_on")

    for torrent in torrentlist:
        name = str(torrent["name"])
        tags = [tag.strip() for tag in str(torrent["tags"]).split(",")]
        newtags = []
        case_sensitive = ["720p", "1080p", "2160p", "HDR"]
        case_insensitive = ["ATMOS", "AV1", "EAC3", "TrueHD", "OPUS", "IMAX"]
        regex = [
            {"pattern": r"4k", "tag": "2160p"},
            {"pattern": r"10bit", "tag": "HDR"},
            {"pattern": r"true-hd", "tag": "TrueHD"},
            {"pattern": r"e-ac3", "tag": "EAC3"},
            {"pattern": r"ddp", "tag": "EAC3"},
            {"pattern": r"dd\+", "tag": "EAC3"},
            {"pattern": r"[^a-z]dd[^a-z+]", "tag": "AC3"},
            {"pattern": r"[^e]ac3", "tag": "AC3"},
            {"pattern": r"dts[^-hx]", "tag": "DTS"},
            {"pattern": r"dts-?hd.[^ma]|dts-?hd$", "tag": "DTS-HD"},
            {"pattern": r"dts-hd.ma", "tag": "DTS-HD MA"},
            {"pattern": r"dts-x", "tag": "DTS-X"},
            {"pattern": r"german", "tag": "GER"},
            {"pattern": r"[-. ]ger", "tag": "GER"},
            {"pattern": r"[-. ]avc[-. ]", "tag": "H.264"},
            {"pattern": r"x264", "tag": "H.264"},
            {"pattern": r"h264", "tag": "H.264"},
            {"pattern": r"h\.264", "tag": "H.264"},
            {"pattern": r"hevc", "tag": "H.265"},
            {"pattern": r"x265", "tag": "H.265"},
            {"pattern": r"h265", "tag": "H.265"},
            {"pattern": r"h\.265", "tag": "H.265"},
        ]
        for pattern in case_sensitive:
            if pattern in name:
                if pattern not in tags:
                    newtags.append(pattern)
        for pattern in case_insensitive:
            if pattern.lower() in name.lower():
                if pattern not in tags:
                    newtags.append(pattern)
        for pattern in regex:
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
        with open(configpath, "w", encoding="utf-8") as f:
            for name in knowntorrents:
                f.write(name + os.linesep)


if __name__ == "__main__":
    main()
