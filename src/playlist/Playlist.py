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

# If verbose and/or debug are set this many times, this is the resulting log level.
LOG_DEBUG = 2
LOG_INFO = 1
LOG_WARNING = 0

# Set up a specific logger with our desired output level
log = logging.getLogger("__main__")


# Regular expressions.
MP3_FILENAME = re.compile(r".*?\.mp3$")

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
            mp3_filename = os.path.join(dirpath, filename)
            if guessMimetype(mp3_filename) in MIME_TYPES:
                relpath = os.path.relpath(dirpath, args.media)
                rel_filename = os.path.join(relpath, filename)
                if filterMedia(mp3_filename):
                    mediaList.append(rel_filename)
                    # print(dirpath)
                    # print(relpath)
                    # print(mp3_filename)
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
        mp3 = eyed3.load(filename)

        duration = mp3.info.time_secs
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

def generate_playlist_filename(directory, output, format):
    if output:
        # Base64 encode the output.
        if args.base64:
            output = base64.b64encode(output.encode("utf-8")).decode("utf-8")
            output = "%s.%s" % (output, args.format)
        return os.path.join(directory, output)
    else:
        fileTimestamp = time.strftime("%Y%m%d%H%M%S")
        filename = "%splaylist" % fileTimestamp
        if args.base64:
            filename = base64.b64encode(filename.encode("utf-8")).decode("utf-8")
        filename = "%s.%s" % (filename, format)
        return os.path.join(directory, filename)

def write_playlist(filename, format, mediaList, randomList, separator):
    log.info("Writing your playlist to '%s'..." % filename)
    nameTimestamp = time.strftime("%Y-%m-%d %H.%M.%S")
    if not args.root:
        setattr(args, "root", args.media)
    with open(filename, "w") as playlist:
       if format == "wpl":
           playlist.write('<?wpl version="1.0"?>\n')
           playlist.write("<smil>\n")
           playlist.write("    <head>\n")
           playlist.write("        <title>%s</title>\n" % nameTimestamp)
           playlist.write("    </head>\n")
           playlist.write("    <body>\n")
           playlist.write("        <seq>\n")
           for ii in randomList:
               mp3_filename = os.path.join(args.root, mediaList[ii])
               if args.separator != os.sep:
                   mp3_filename = mp3_filename.replace(os.sep, args.separator)
               playlist.write('            <media src="')
               playlist.write(escapeXml(mp3_filename))
               playlist.write('" />\n')
           playlist.write("        </seq>\n")
           playlist.write("    </body>\n")
           playlist.write("</smil>\n")
       else:
           if args.format == "m3u":
                    playlist.write("#EXTM3U\n\n")
                    playlist.write("#PLAYLIST:%s\n" % nameTimestamp)
           else:
                    playlist.write("#EXTM3UP\n")
           for ii in randomList:
               mp3_filename = os.path.join(args.media, mediaList[ii])
               # print(args.media)
               # print(mediaList[ii])
               # print(mp3_filename)
               # sys.exit(8)
               mp3 = eyed3.load(mp3_filename)
               # Note we might want to write a different root to the playlist
               mp3_filename = os.path.join(args.root, mediaList[ii])
               # print(os.sep)
               # print(args.separator)
               # sys.exit(7)
               #print(mp3_filename)
               if separator != os.sep:
                   mp3_filename = mp3_filename.replace(os.sep, separator)
               #print(mp3_filename
               playlist.write(
                   "EXTINF:%d, %s - %s\n"
                   % (mp3.info.time_secs, mp3.tag.artist, mp3.tag.title)
               )
               playlist.write(escapeXml(mp3_filename))
               #print(mp3_filename)
               playlist.write("\n")
               if args.format == "m3u":
                    playlist.write("\n")

def maybeDeleteOldPlaylist():
    """Delete old playlists."""
    log.info("Playlists in...: '%s'..." % args.playlist)

    # Windows Media Player doesn't seem to like complex filenames.
    PLAYLIST = re.compile(r"(?P<date>\d{8})" r"(?P<time>\d{6})playlist.(?P<ext>\w+)")

    playlists = list_playlists(args.playlist, PLAYLIST)
    delete_old_playlists(args.playlist, playlists, args.limit)


def writePlaylist(mediaList, randomList):
    """Write the playlist to the appropriate file."""
    filename = generate_playlist_filename(args.playlist, args.output, args.format)
    write_playlist(filename, args.format, mediaList, randomList, args.separator)


def main():
    """Mainline function."""
    mediaList = buildMediaList()
    randomList = selectMedia(mediaList)
    if len(randomList) > 0:
        maybeDeleteOldPlaylist()
        writePlaylist(mediaList, randomList)


def argparser():
    """
    Build an arguments parser.

    :returns: An arguments parser.
    :rtype: Parser
    """
    parser = argparse.ArgumentParser(description="Create randomized playlists")
    parser.add_argument(
        "-f", "--format", choices=["m3u", "wpl", "m3up"], default="m3u", help="playlist format"
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
    parser.add_argument("-m", "--media", default=".", help="root directory from which to source media")
    parser.add_argument("-r", "--root", help="root to show in media filenames")
    parser.add_argument(
        "-p", "--playlist", default=".", help="root directory for playlists"
    )
    # Create mutually exclusive group for tracks and duration
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        "--tracks",
        type=int,
        default=0,
        help="number of tracks for playlist"
    )
    group.add_argument(
        "-d",
        "--duration",
        type=int,
        default=0,
        help="total playing time duration (minutes)"
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

    return parser


if __name__ == "__main__":
    """ """
    verbosity_level = 1
    log_level = logging.ERROR

    # Parse command line arguments.
    parser = argparser()
    args = parser.parse_args()
    if not args.duration and not args.tracks:
        print("At least one limit must be set")
        sys.exit(9)
    # print(args)

    # Convert arguments where appropriate
    SECONDS_PER_MINUTE = 60
    args.duration = args.duration * SECONDS_PER_MINUTE
    if args.before is not None:
        args.before = eyed3.core.Date(args.before)
    if args.after is not None:
        args.after = eyed3.core.Date(args.after)

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
    log.info("Entry {")
    main()
    log.info("Exit {")
    logging.shutdown()
