#!/usr/bin/python3
"""Script to create an MP3 playlist for media players."""

from __future__ import print_function
import argparse
import logging
import os
import re
import random
from eyed3.id3 import Tag
from eyed3.mimetype import guessMimetype
from eyed3.mp3 import MIME_TYPES
import eyed3
import time
import sys
import base64
from typing import TextIO, Any, List

# If verbose and/or debug are set this many times, this is the resulting log level.
LOG_DEBUG = 2
LOG_INFO = 1
LOG_WARNING = 0

# Set up a specific logger with our desired output level
log = logging.getLogger("__main__")


# Regular expressions.
mp3_track = re.compile(r".*?\.mp3_data$")

# MP3 IDv1 genres.
GENRES = [
    "Blues",
    "Alternative",
    "AlternRock",
    "Top 40",
    "Folk",
    "Opera",
    "Classic Rock",
    "Ska",
    "Bass",
    "Christian Rap",
    "Folk-Rock",
    "Chamber Music",
    "Country",
    "Death Metal",
    "Soul",
    "Pop/Funk",
    "National Folk",
    "Sonata",
    "Dance",
    "Pranks",
    "Punk",
    "Jungle",
    "Swing",
    "Symphony",
    "Disco",
    "Soundtrack",
    "Space",
    "Native American",
    "Fast Fusion",
    "Booty Bass",
    "Funk",
    "Euro-Techno",
    "Meditative",
    "Cabaret",
    "Bebob",
    "Primus",
    "Grunge",
    "Ambient",
    "Instrumental Pop",
    "New Wave",
    "Latin",
    "Porn Groove",
    "Hip-Hop",
    "Trip-Hop",
    "Instrumental Rock",
    "Psychadelic",
    "Revival",
    "Satire",
    "Jazz",
    "Vocal",
    "Ethnic",
    "Rave",
    "Celtic",
    "Slow Jam",
    "Metal",
    "Jazz+Funk",
    "Gothic",
    "Showtunes",
    "Bluegrass",
    "Club",
    "New Age",
    "Fusion",
    "Darkwave",
    "Trailer",
    "Avantgarde",
    "Tango",
    "Oldies",
    "Trance",
    "Techno-Industrial",
    "Lo-Fi",
    "Gothic Rock",
    "Samba",
    "Other",
    "Classical",
    "Electronic",
    "Tribal",
    "Progressive Rock",
    "Folklore",
    "Pop",
    "Instrumental",
    "Pop-Folk",
    "Acid Punk",
    "Psychedelic Rock",
    "Ballad",
    "R&B",
    "Acid",
    "Eurodance",
    "Acid Jazz",
    "Symphonic Rock",
    "Power Ballad",
    "Rap",
    "House",
    "Dream",
    "Polka",
    "Slow Rock",
    "Rhythmic Soul",
    "Reggae",
    "Game",
    "Southern Rock",
    "Retro",
    "Big Band",
    "Freestyle",
    "Rock",
    "Sound Clip",
    "Comedy",
    "Musical",
    "Chorus",
    "Duet",
    "Techno",
    "Gospel",
    "Cult",
    "Rock & Roll",
    "Easy Listening",
    "Punk Rock",
    "Industrial",
    "Noise",
    "Gangsta",
    "Hard Rock",
    "Acoustic",
    "Drum Solo",
    "Humour",
    "A capella",
    "Speech",
    "Euro-House",
    "Chanson",
    "Dance Hall",
]


def escapeXml(raw):
    """Escape an XML string otherwise some media clients crash."""
    # Note that we deliberately convert ampersand first so that it is not
    # confused for anything else.
    mapping = [
        ("&", "&amp;"),
        ("<", "&lt;"),
        (">", "&gt;"),
        ('"', "&quot;"),
        ("'", "&apos;"),
    ]
    for k, v in mapping:
        raw = raw.replace(k, v)

    return raw


def filterMedia(filename):
    """Fileter the media based on the provided criteria."""
    accept = False

    mp3Tags = Tag()
    mp3Tags.parse(filename)
    # if mp3File:
    #     mp3Tags = mp3File.id3.Tag

    bestDate = mp3Tags.getBestDate()
    genre = mp3Tags.genre

    if args.genre is None or (genre is not None and genre.name in args.genre):
        # Genre passes
        if args.before is None or bestDate is None or bestDate < args.before:
            # Before date passes
            if args.after is None or bestDate is None or bestDate > args.after:
                # After date passes
                accept = True

    return accept


def buildMediaList():
    """Build the list of available media."""
    mediaList = []

    log.info("Walking media tree rooted at '%s'..." % args.media)

    for dirpath, dirnames, filenames in os.walk(args.media):
        log.debug("Directory: '%s'..." % dirpath)
        log.debug("Dirnames:  '%s'..." % dirnames)
        log.debug("Filenames: '%s'..." % filenames)

        for filename in filenames:
            log.debug("filename: %s", filename)
            mp3_track = os.path.join(dirpath, filename)
            if guessMimetype(mp3_track) in MIME_TYPES:
                relpath = os.path.relpath(dirpath, args.media)
                rel_filename = os.path.join(relpath, filename)
                if filterMedia(mp3_track):
                    mediaList.append(rel_filename)
                    # print(dirpath)
                    # print(relpath)
                    # print(mp3_track)
                    # sys.exit(9)

    log.debug(mediaList)
    return mediaList


def selectMedia(mediaList):
    """Select which media we will include in the playlist."""
    log.info("Selecting tracks for your playlist...")

    randomList = []

    log.debug(mediaList)
    log.debug(len(mediaList))
    mediaLen = len(mediaList) - 1
    maxTracks = args.tracks

    if (mediaLen / 2) < maxTracks:
        log.info("Limiting playlist to %d tracks..." % maxTracks)
        maxTracks = mediaLen / 2

    tracksFound = 0
    totalDuration = 0

    random.seed()
    while True:
        randomTrack = random.randint(0, mediaLen)
        while randomTrack in randomList:
            randomTrack = random.randint(0, mediaLen)
        randomList.append(randomTrack)
        tracksFound = tracksFound + 1

        # Now that we have decided to add the track, how long is it and
        # how long does this make our playlist?
        filename = os.path.join(args.media, mediaList[randomTrack])
        mp3_data = eyed3.load(filename)

        duration = mp3_data.info.time_secs
        totalDuration = totalDuration + duration

        if maxTracks and tracksFound >= maxTracks:
            # Track limit has been reached.
            log.info("Track limit reached")
            break

        if args.duration and totalDuration >= args.duration:
            # Time limit has been reached.
            log.info("Time limit reached")
            break

    log.info("Playlist contains %d tracks" % len(randomList))
    return randomList


def list_playlists(directory, pattern):
    playlists = []
    for filename in os.listdir(directory):
        m = pattern.match(filename)
        if m:
            playlists.append(filename)
    return playlists


def delete_old_playlists(directory, playlists, limit):
    if limit:
        log.info("Deleting old playlists...")
        to_delete = len(playlists) - limit
        if to_delete > 0:
            log.info("Delete %d playlists..." % to_delete)
            playlists.sort()
            for td in range(0, to_delete):
                fullname = os.path.join(directory, playlists[td])
                log.info("Deleting old playlist: %s" % fullname)
                os.remove(fullname)


def generate_playlist_filename(args):
    filename: str
    playlist_name: str
    if args.output:
        playlist_name = args.output
    else:
        fileTimestamp: str = time.strftime("%Y%m%d%H%M%S")
        playlist_name = "%splaylist" % fileTimestamp

    # Base64 encode the output.
    if args.base64:
        playlist_name = base64.b64encode(playlist_name.encode("utf-8")).decode("utf-8")

    filename = os.path.join(args.playlist, playlist_name + "." + args.format)
    return playlist_name, filename


class Playlist:
    def __init__(self, playlist_name: str, filename: str) -> None:
        self.playlist_name: str = playlist_name
        self.filename: str = filename
        self.format: str = ""
        self.ext: str = ""
        self.playlist: TextIO = None

    def Open(self) -> None:
        self.playlist = open(self.filename, "w")

    def Close(self) -> None:
        self.playlist.close()

    def WriteHeader(self) -> None:
        raise NotImplementedError

    def WriteFooter(self) -> None:
        raise NotImplementedError

    def WriteTrack(self, mp3_track: str, mp3_data: Any) -> None:
        mp3_track = mp3_track
        mp3_data = mp3_data
        raise NotImplementedError


class M3UPlaylist(Playlist):
    def __init__(self, playlist_name: str, filename: str) -> None:
        super().__init__(playlist_name, filename)
        self.format: str = "EXTM3U"

    def WriteHeader(self):
        self.playlist.write("#EXT%s\n" % self.format.upper())
        self.playlist.write("#PLAYLIST:%s\n" % self.playlist_name)

    def WriteFooter(self):
        pass

    def WriteTrack(self, mp3_track: str, mp3_data: Any):
        self.playlist.write(
            "EXTINF:%d, %s - %s\n"
            % (mp3_data.info.time_secs, mp3_data.tag.artist, mp3_data.tag.title)
        )
        self.playlist.write(escapeXml(mp3_track))
        self.playlist.write("\n")


class M3UPPlaylist(M3UPlaylist):
    def __init__(self, playlist_name: str, filename: str) -> None:
        super().__init__(playlist_name, filename)
        self.format: str = "EXTM3U8"


class WPLPlaylist(Playlist):
    def WriteHeader(self) -> None:
        self.playlist.write('<?wpl version="1.0"?>\n')
        self.playlist.write("<smil>\n")
        self.playlist.write("    <head>\n")
        self.playlist.write("        <title>%s</title>\n" % self.playlist_name)
        self.playlist.write("    </head>\n")
        self.playlist.write("    <body>\n")
        self.playlist.write("        <seq>\n")

    def WriteFooter(self):
        self.playlist.write("        </seq>\n")
        self.playlist.write("    </body>\n")
        self.playlist.write("</smil>\n")

    def WriteTrack(self, mp3_track: str, _: Any):
        self.playlist.write('            <media src="')
        self.playlist.write(escapeXml(mp3_track))
        self.playlist.write('" />\n')


def write_playlist(
    args, playlist_name, filename, mediaList: List[str], randomList: List[int]
):
    log.info("Writing your playlist to '%s'..." % filename)
    root: str = args.root
    if not args.root:
        root = args.media

    playlistMap = {"m3u": M3UPlaylist, "m3up": M3UPPlaylist, "wpl": WPLPlaylist}

    playlist: Playlist = playlistMap[args.format](playlist_name, filename)

    playlist.Open()
    playlist.WriteHeader()
    ii: int
    for ii in randomList:
        mp3_track: str = os.path.join(root, mediaList[ii])
        mp3_filename: str = os.path.join(args.media, mediaList[ii])
        if args.separator != os.sep:
            mp3_track = mp3_track.replace(os.sep, args.separator)
        mp3_data: Any = eyed3.load(mp3_filename)
        playlist.WriteTrack(mp3_track, mp3_data)
    playlist.WriteFooter()
    playlist.Close()


def maybeDeleteOldPlaylist(args):
    """Delete old playlists."""
    log.info("Playlists in...: '%s'..." % args.playlist)

    # Windows Media Player doesn't seem to like complex filenames.
    PLAYLIST = re.compile(r"(?P<date>\d{8})" r"(?P<time>\d{6})playlist.(?P<ext>\w+)")

    playlists = list_playlists(args.playlist, PLAYLIST)
    delete_old_playlists(args.playlist, playlists, args.limit)


def writePlaylist(args, mediaList, randomList):
    """Write the playlist to the appropriate file."""
    playlist_name, filename = generate_playlist_filename(args)
    write_playlist(args, playlist_name, filename, mediaList, randomList)


def main():
    """Mainline function."""
    mediaList = buildMediaList()
    randomList = selectMedia(mediaList)
    if len(randomList) > 0:
        maybeDeleteOldPlaylist(args)
        writePlaylist(args, mediaList, randomList)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """
    Build an arguments parser.

    :returns: An arguments parser.
    :rtype: Parser
    """
    parser = argparse.ArgumentParser(description="Create randomized playlists")
    parser.add_argument(
        "-f",
        "--format",
        choices=["m3u", "wpl", "m3up"],
        default="m3u",
        help="playlist format",
    )
    parser.add_argument("-o", "--output", default=None, help="playlist filename")
    parser.add_argument(
        "-b", "--before", type=int, default=None, help="only tracks from before (year)"
    )
    parser.add_argument(
        "-a", "--after", type=int, default=None, help="only tracks from after (year)"
    )
    parser.add_argument(
        "-g",
        "--genre",
        default=["Pop"],
        action="append",
        help="music genre(s) for tracks",
    )
    parser.add_argument(
        "-m", "--media", default=".", help="root directory from which to source media"
    )
    parser.add_argument("-r", "--root", help="root to show in media filenames")
    parser.add_argument(
        "-p", "--playlist", default=".", help="root directory for playlists"
    )
    # Create mutually exclusive group for tracks and duration
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-t", "--tracks", type=int, default=0, help="number of tracks for playlist"
    )
    group.add_argument(
        "-d",
        "--duration",
        type=int,
        default=0,
        help="total playing time duration (minutes)",
    )

    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=0,
        help="maximum number of playlists; oldest is deleted if required",
    )
    parser.add_argument(
        "-x",
        "--debug",
        action="count",
        default=0,
        help="debug setting for trace file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="verbose mode showing what we're doing",
    )
    parser.add_argument(
        "-s",
        "--separator",
        default=os.sep,
        help="Directory separator to use for filenames",
    )
    parser.add_argument(
        "-e",
        "--base64",
        action="store_true",
        help="Base64 encode the filename",
    )

    args: argparse.Namespace = parser.parse_args(argv[1:])

    # Convert arguments where appropriate
    SECONDS_PER_MINUTE: int = 60
    args.duration = args.duration * SECONDS_PER_MINUTE
    if args.before is not None:
        args.before = eyed3.core.Date(args.before)
    if args.after is not None:
        args.after = eyed3.core.Date(args.after)

    return args


if __name__ == "__main__":
    """ """
    verbosity_level = 1
    log_level = logging.ERROR

    # Parse command line arguments.
    args = parse_args(sys.argv)

    # Set log level.
    if args.verbose >= LOG_DEBUG:
        log_level = logging.DEBUG
    elif args.verbose >= LOG_INFO:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    FORMAT = "%(asctime)-15s %(filename)s:%(lineno)d %(funcName)s %(message)s"
    logging.basicConfig(
        filename="Playlist.log", filemode="w", format=FORMAT, level=log_level
    )

    # now actually run the tests.
    main()
    logging.shutdown()
