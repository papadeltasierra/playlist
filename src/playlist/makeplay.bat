echo on
if %3.==. goto :HELP
set NAME=%1
set DIR=%2
set DURATION=%3

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
set GENRE=%GENRE% --genre "Motown"
set GENRE=%GENRE% --genre Soul
set GENRE=%GENRE% --genre "Surf Pop"
python c:\users\pds\git\playlist\playlist\Playlist.py --format wpl %GENRE% --media d:\users\pds\music --playlist %DIR% --duration %DURATION%
popd
pushd c:\users\pds\python\playlist
call scripts\deactivate
popd
pushd %DIR%
cd
ren ??????????????playlist.wpl %NAME%
popd
goto :EOF

:HELP
echo Usage: makeplay <name> <dir> <duration>
echo.
echo duration - Time to play for (minutes)
goto :EOF

:EOF
