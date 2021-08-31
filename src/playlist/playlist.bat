pushd c:\users\pds\python\playlist
call scripts\activate
set GENRE=--genre Pop
set GENRE=%GENRE% --genre "Classic Rock"
set GENRE=%GENRE% --genre Disco
set GENRE=%GENRE% --genre "Folk/Rock"
set GENRE=%GENRE% --genre Motown
set GENRE=%GENRE% --genre "New Wave"
set GENRE=%GENRE% --genre Oldies
set GENRE=%GENRE% --genre Rock
set GENRE=%GENRE% --genre "Rock & Roll"
set GENRE=%GENRE% --genre "Pop/Rock"
set GENRE=%GENRE% --genre Soul
set GENRE=%GENRE% --genre Motown
set GENRE=%GENRE% --genre "Surf Pop"
python c:\users\pds\git\playlist\playlist\Playlist.py --format wpl %GENRE% --media d:\users\pds\music --playlist d:\users\pds\music\Playlists --tracks 60 --limit 20
popd
pushd c:\users\pds\python\playlist
call scripts\deactivate
popd
REM exit