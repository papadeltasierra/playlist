# Playlist
A random playlist generator.
## Dependencies
Uses the [eyeD3][eyeD3] MP3 parsing library.
## Usage
```
$ playlist -?
usage: playlist.py [-h] [-?] [-f {m3u,wpl}] [-b BEFORE] [-a AFTER]
                   [-d DURATION] [-g GENRE] [-m MEDIA] [-p PLAYLIST]
                   [-t TRACKS] [-l LIMIT] [-v]

Create randomized playlists

optional arguments:
  -h, --help            show this help message and exit
  -?, --query           show this help message and exit
  -f {m3u,wpl}, --format {m3u,wpl}
                        playlist format
  -b BEFORE, --before BEFORE
                        only tracks from before (year)
  -a AFTER, --after AFTER
                        only tracks from after (year)
  -d DURATION, --duration DURATION
                        total playing time duration (minutes)
  -g GENRE, --genre GENRE
                        music genre(s) for tracks
                        
                        
  -m MEDIA, --media MEDIA
                        root directory for media
  -p PLAYLIST, --playlist PLAYLIST
                        root directory for playlists
  -t TRACKS, --tracks TRACKS
                        numer of tracks for playlist
  -l LIMIT, --limit LIMIT
                        maximum number of playlists; oldest is deleted if
                        required
  -v, --verbose         verbose mode showing what we're doing
        default="m3u", help="playlist format")
    parser.add_argument(
        "-b", "--before", type=int, default=None,
        help="only tracks from before (year)")
    parser.add_argument(
        "-a", "--after", type=int, default=None,
        help="only tracks from after (year)")
    parser.add_argument(
        "-d", "--duration", type=int, default=60,
        help="total playing time duration (minutes)")
    parser.add_argument(
        "-g", "--genre", default=["Pop"], action='append',
        help="music genre(s) for tracks")
    parser.add_argument(
        "-m", "--media", default=".",
        help="root directory for media")
    parser.add_argument(
        "-p", "--playlist", default=".",
        help="root directory for playlists")
    parser.add_argument(
        "-t", "--tracks", type=int, default=20,
        help="numer of tracks for playlist")
    parser.add_argument(
        "-l", "--limit", type=int, default=10,
        help="maximum number of playlists; oldest is deleted if required")
    parser.add_argument(
        "-v", "--verbose", action="store_const", const=True, default=False,
        help="verbose mode showing what we're doing")
```

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [eyeD3]: <http://eyed3.nicfit.net/>
