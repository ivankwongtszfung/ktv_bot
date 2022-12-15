# ktv_bot
Just a lazy approach to download mv from internet

# usage
given a list of songs/singers, we will automatically downloaded all the files found in the sites.
# Environment Variable
| Name            | description        |
| --------------- | ------------------ |
| MVXZ_URL        | link to mvxz.com   |
| CTFILE_URL      | link to ctfile.com |
| SONG_LOCAL_PATH | songs folder       |
# How to run the program
## for linux
```sh
. venv/bin/activate
python get_songs.py <list of songs/singers delimited by space>
```
## window
```ps1
# in powershell
Set-ExecutionPolicy Unrestricted -Scope Process -force
venv/Script/activate
python get_songs.py <list of songs/singers delimited by space>
```
```cmd
venv/Script/activate.bat
python get_songs.py <list of songs/singers delimited by space>
```