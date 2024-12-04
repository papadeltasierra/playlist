import pytest
from unittest.mock import patch, mock_open
import os
import re
import time
from src.playlist.playlist import list_playlists, delete_old_playlists, generate_playlist_filename, write_playlist

@patch('os.listdir')
def test_list_playlists(mock_listdir):
    mock_listdir.return_value = ['20230101120000playlist.wpl', '20230101130000playlist.wpl', 'otherfile.txt']
    pattern = re.compile(r"(?P<date>\d{8})(?P<time>\d{6})playlist.(?P<ext>\w+)")
    playlists = list_playlists(os.path.join('fake', 'dir'), pattern)
    assert playlists == ['20230101120000playlist.wpl', '20230101130000playlist.wpl']

@patch('os.remove')
def test_delete_old_playlists(mock_remove):
    playlists = ['20230101120000playlist.wpl', '20230101130000playlist.wpl']
    delete_old_playlists(os.path.join('fake', 'dir'), playlists, 1)
    mock_remove.assert_called_once_with(os.path.join('fake', 'dir', '20230101120000playlist.wpl'))

@patch('time.strftime')
def test_generate_playlist_filename_with_output(mock_strftime):
    filename = generate_playlist_filename(os.path.join('fake', 'dir'), 'output.wpl', 'wpl')
    assert filename == os.path.join('fake', 'dir', 'output.wpl')

@patch('time.strftime')
def test_generate_playlist_filename_without_output(mock_strftime):
    mock_strftime.return_value = '20230101120000'
    filename = generate_playlist_filename(os.path.join('fake', 'dir'), None, 'wpl')
    assert filename == os.path.join('fake', 'dir', '20230101120000playlist.wpl')

@patch('builtins.open', new_callable=mock_open)
def test_write_playlist(mock_open):
    filename = os.path.join('fake', 'dir', 'playlist.wpl')
    format = 'wpl'
    mediaList = []
    randomList = []
    write_playlist(filename, format, mediaList, randomList)
    mock_open.assert_called_once_with(filename, 'w')
    mock_open().write.assert_called_once_with('<?wpl version="1.0"?>\n')

if __name__ == '__main__':
    pytest.main()