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

        for filename in filenames:
            log.debug("filename: %s", filename)
            full_filename = os.path.join(dirpath, filename)
            # if eyed3.mp3.isMp3File(filename):
            mp3_filename = os.path.join(dirpath, filename)
            if guessMimetype(mp3_filename) in MIME_TYPES:
                relpath = os.path.relpath(dirpath, args.playlist)
                rel_filename = os.path.join(relpath, filename)
                if filterMedia(mp3_filename):
                    mediaList.append(rel_filename)

    # print(mediaList)
    return mediaList


def selectMedia(mediaList):
    """Select which media we will include in the playlist."""
    log.info("Selecting tracks for your playlist...")

    randomList = []

    # print(mediaList)
    # print(len(mediaList))
    mediaLen = len(mediaList) - 1
    maxTracks = args.tracks

    if (mediaLen / 2) < maxTracks:
        log.info("Limiting playlist to %d tracks..." % maxTracks)
        maxTracks = mediaLen / 2

    if maxTracks > 0:
        log.info("Your playlist will have %d tracks..." % maxTracks)

        tracksFound = 0
        totalDuration = 0

        random.seed()
        while tracksFound < maxTracks:
            randomTrack = random.randint(0, mediaLen)
            # print(randomTrack)
            # print(str(randomList))
            while randomTrack in randomList:
                randomTrack = random.randint(0, mediaLen)
            randomList.append(randomTrack)
            tracksFound = tracksFound + 1

            # Now that we have decided to add the track, how long is it and
            # how long does this make our playlist?
            filename = os.path.join(args.playlist, mediaList[randomTrack])
            mp3 = eyed3.load(filename)

            duration = mp3.info.time_secs

            totalDuration = totalDuration + duration
            if totalDuration >= args.duration:
                # Time limit has been reached.
                break
    else:
        log.error("Too few tracks were found to allow creation of a playlist.")

    return randomList


def maybeDeleteOldPlaylist():
    """Delete old playlists."""
    log.info("Playlists in...: '%s'..." % args.playlist)

    # Windows Media Player doesn't seem to like complex filenames.
    PLAYLIST = re.compile(r"(?P<date>\d{8})" r"(?P<time>\d{6})playlist.(?P<ext>\w+)")

    playlists = []

    for filename in os.listdir(args.playlist):
        m = PLAYLIST.match(filename)
        if m:
            playlists.append(filename)

    to_delete = (len(playlists) + 1) - args.limit
    if to_delete > 0:
        # Need to delete some playlists.
        log.info("Delete %d playlists..." % to_delete)
        playlists.sort()

        for td in range(0, to_delete):
            fullname = os.path.join(args.playlist, playlists[td])
            log.info("Deleting old playlist: %s" % fullname)
            os.remove(fullname)


def writePlaylist(mediaList, randomList):
    """Write the playlist to the appropriate file."""
    # Playlist filename is a datestamp etc.
    fileTimestamp = time.strftime("%Y%m%d%H%M%S")
    nameTimestamp = time.strftime("%Y-%m-%d %H.%M.%S")
    filename = "%splaylist.%s" % (fileTimestamp, args.format)
    filename = os.path.join(args.playlist, filename)

    log.info("Writing your playlist to '%s'..." % filename)

    with open(filename, "w") as playlist:
        if args.format == "wpl":
            playlist.write('<?wpl version="1.0"?>\n')
            playlist.write("<smil>\n")
            playlist.write("    <head>\n")
            playlist.write("        <title>%s</title>\n" % nameTimestamp)
            playlist.write("    </head>\n")
            playlist.write("    <body>\n")
            playlist.write("        <seq>\n")

            for ii in randomList:
                playlist.write('            <media src="')
                playlist.write(escapeXml(mediaList[ii]))
                playlist.write('" />\n')

            playlist.write("        </seq>\n")
            playlist.write("    </body>\n")
            playlist.write("</smil>\n")
        else:
            playlist.write("#EXTM3U\n\n")
            for ii in randomList:
                mp3_filename = os.path.join(args.playlist, mediaList[ii])
                mp3 = eyed3.load(mp3_filename)
                playlist.write("EXTINF:%d, %s - %s\n" % (mp3.info.time_secs, mp3.tag.artist, mp3.tag.title))
                playlist.write(escapeXml(mediaList[ii]))
                playlist.write("\n\n")


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
        "-f", "--format", choices=["m3u", "wpl"], default="m3u", help="playlist format"
    )
    parser.add_argument(
        "-b", "--before", type=int, default=None, help="only tracks from before (year)"
    )
    parser.add_argument(
        "-a", "--after", type=int, default=None, help="only tracks from after (year)"
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=60,
        help="total playing time duration (minutes)",
    )
    parser.add_argument(
        "-g",
        "--genre",
        default=["Pop"],
        action="append",
        help="music genre(s) for tracks",
    )
    parser.add_argument("-m", "--media", default=".", help="root directory for media")
    parser.add_argument(
        "-p", "--playlist", default=".", help="root directory for playlists"
    )
    parser.add_argument(
        "-t", "--tracks", type=int, default=20, help="numer of tracks for playlist"
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=10,
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

    return parser


if __name__ == "__main__":
    """ """
    verbosity_level = 1
    log_level = logging.ERROR

    # Parse command line arguments.
    parser = argparser()
    args = parser.parse_args()

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
