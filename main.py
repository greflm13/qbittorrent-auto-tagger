import re
import argparse

import qbittorrentapi


def argpar():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--host", help="qbittorrent url", required=True, type=str, dest="host")
    parser.add_argument("-o", "--port", help="qbittorrent port", required=False, type=int, dest="port", default=80)
    parser.add_argument("-u", "--user", help="qbittorrent user", required=True, type=str, dest="user")
    parser.add_argument("-p", "--password", help="qbittorrent password", required=True, type=str, dest="passw")
    return parser.parse_args()


def main():
    args = argpar()

    client = qbittorrentapi.Client(host=args.host, port=args.port, username=args.user, password=args.passw)
    client.auth_log_in()

    torrentlist = client.torrents.info(sort="added_on")

    for torrent in torrentlist:
        name = torrent["name"]
        tags = [tag.strip() for tag in torrent["tags"].split(",")]
        newtags = []
        case_sensitive = ["720p", "1080p", "2160p", "HDR"]
        case_insensitive = ["ATMOS", "AV1", "EAC3", "TrueHD", "OPUS", "IMAX"]
        regex = [
            {"pattern": r"4k", "tag": "2160p"},
            {"pattern": r"10bit", "tag": "HDR"},
            {"pattern": r"e-ac3", "tag": "EAC3"},
            {"pattern": r"[^e]ac3", "tag": "AC3"},
            {"pattern": r"dts[^-h]", "tag": "DTS"},
            {"pattern": r"dts-?hd.[^m]", "tag": "DTS-HD"},
            {"pattern": r"dts-hd.ma", "tag": "DTS-HD MA"},
            {"pattern": r"german", "tag": "GER"},
            {"pattern": r"[-. ]ger", "tag": "GER"},
            {"pattern": r"[-. ]avc[-. ]", "tag": "H.264"},
            {"pattern": r"x264", "tag": "H.264"},
            {"pattern": r"hevc", "tag": "H.265"},
            {"pattern": r"x265", "tag": "H.265"},
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
        if len(newtags) > 0:
            print(f"adding tags to {name}: {', '.join(set(newtags))}")
            torrent.add_tags(set(newtags))

    client.auth_log_out()


if __name__ == "__main__":
    main()
