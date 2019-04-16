from os.path import (expanduser, expandvars, normpath, abspath)


def print_help(*args, short=False, **kwargs):
    usage = """
youtube-subscribe v{version}

Usage:
  python3 {filename} add [--overwrite] <playlist-url>|<playlist-id>
  python3 {filename} ls [--short] [<playlist-id-matcher>]
  python3 {filename} rm --all|<playlist-id-matcher>
  python3 {filename} dl [--sync] [<playlist-id-matcher> [<episode>]]

Description:
  <playlist-id> := string starts with 'PL'
  <playlist-url> := https://www.youtube.com/(watch|playlist)?list=<playlist-id>
  <playlist-id-matcher> :=
    substring of <playlist-id> that identify THE ONLY playlist

  <episode> := int|int-int|<episode>,<episode>
  <episode> should not contains any space
"""

    example = """
Examples:
  # add by <playlist-id>
  python3 {filename} add PLabc123456defg

  # add by <playlist-id> or overwrite the playlist if existed
  python3 {filename} add --overwrite PLabc123456defg

  # add by <playlist-url>
  python3 {filename} add https://www.youtube.com/playlist?list=PLabc654321defg

  ### Now we have 2 playlist [PLabc123456defg, PLabc654321defg]

  # list all playlists
  python3 {filename} ls

  # list all playlists in summary
  python3 {filename} ls --short

  # *BAD*, match multiple playlists
  python3 {filename} ls abc

  # *GOOD*, list PLabc123456defg
  python3 {filename} ls 6d

  # download all episodes that not downloaded in all playlists
  python3 {filename} dl

  # do above after synchronize all playlists on youtube
  python3 {filename} dl --sync

  # download all episodes that not downloaded in playlist PLabc123456defg
  python3 {filename} dl c1

  # do above after synchronize playlist PLabc123456defg on youtube
  python3 {filename} dl c1 --sync

  # download 1,2,3,6-9,11 episodes that not downloaded in playlist PLabc123456defg
  python3 {filename} dl bc1 1,6-9,11,2,3

  # remove playlist PLabc654321defg
  python3 {filename} rm 21

  # remove all playlists
  python3 {filename} rm --all
"""

    if short:
        print((usage).format(*args, **kwargs))
    else:
        print((usage + example).format(*args, **kwargs))


def extract_info(j):
    """
    return info dict

    info = {
        id := str,
        title := str,
        index := int,
        filename := str
        playlist_title := str
    }
    """
    return dict((
        ("id", j["display_id"]),
        ("title", j["title"]),
        ("index", j["playlist_index"]),
        ("filename", j["_filename"]),
        ("playlist_title", j["playlist_title"]),
    ))


def resolve_path(path):
    return normpath(abspath(expanduser(expandvars(path))))


def zfilter(function, iterable):
    return list(filter(function, iterable))
