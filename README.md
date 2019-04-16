# Youtube Subscribe

## Installation

```sh
git clone git@github.com:FlandreDaisuki/youtube-subscribe.git
```

## Usage

```sh
python3 main.py add [--overwrite] <playlist-url>|<playlist-id>
python3 main.py ls [--short] [<playlist-id-matcher>]
python3 main.py rm --all|<playlist-id-matcher>
python3 main.py dl [--sync] [<playlist-id-matcher> [<episode>]]
```

## Examples

```sh
# add by <playlist-id>
python3 main.py add PLabc123456defg

# add by <playlist-id> or overwrite the playlist if existed
python3 main.py add --overwrite PLabc123456defg

# add by <playlist-url>
python3 main.py add https://www.youtube.com/playlist?list=PLabc654321defg

### Now we have 2 playlist [PLabc123456defg, PLabc654321defg]

# list all playlists
python3 main.py ls

# list all playlists in summary
python3 main.py ls --short

# *BAD*, match multiple playlists
python3 main.py ls abc

# *GOOD*, list PLabc123456defg
python3 main.py ls 6d

# download all episodes that not downloaded in all playlists
python3 main.py dl

# do above after synchronize all playlists on youtube
python3 main.py dl --sync

# download all episodes that not downloaded in playlist PLabc123456defg
python3 main.py dl c1

# do above after synchronize playlist PLabc123456defg on youtube
python3 main.py dl c1 --sync

# download 1,2,3,6-9,11 episodes that not downloaded in playlist PLabc123456defg
python3 main.py dl bc1 1,6-9,11,2,3

# remove playlist PLabc654321defg
python3 main.py rm 21

# remove all playlists
python3 main.py rm --all
```

## Docker for download periodically

Build your own image

```sh
cd youtube-subscribe
docker build -f docker/Dockerfile . -t my/youtube-subscribe
```

Example conf.json and docker-compose.yml

```json
{
  "ytsub_dir": "~/.youtube-subscribe",
  "destination": "/downloads",
  "options": {
    "output": "%(playlist)s/%(title)s.%(ext)s",
    "format": "best"
  }
}
```

```yml
version: "3.2"

services:
  ytsub:
    image: my/youtube-subscribe # your image name
    container_name: youtube-subscribe
    volumes:
      # In conf file, you need assign the destination and ytsub_dir
      # Otherwise, the default destination is ~/downloads and
      #   default ytsub_dir is ~/.youtube-subscribe
      - ../conf.json:/ytsub/conf.json
      # Following mount point should match the value of destination key
      #   in conf file
      - ./downloads:/downloads
      # Following mount point should match the value of ytsub_dir key
      #   in conf file
      - ./subscriptions:/root/.youtube-subscribe
    environment:
      # cron schedule string format
      - CRON_FREQ=0 * * * *
```

Then compose up

```sh
docker-compose up -d
```
