import re

SPOTIFY_ITEM_URL_PATTERN = re.compile('^spotify:((album)|(playlist)|(track)|(artist)):\w+$')
ITEM_LINK_PATTERN = re.compile('^https://open\.spotify\.com/((album)|(playlist)|(track)|(artist))/\w+(\?\S+)?$')


def convert_item_link_to_spotify(item_link: str) -> str:
    pattern_match = ITEM_LINK_PATTERN.match(item_link)
    assert pattern_match, 'Item link seems invalid'

    pure_link = re.sub('\?\S+$', '', pattern_match.group())
    spotify_code = re.search('\w+$', pure_link).group(0)
    item_type = re.search('((album)|(playlist)|(track)|(artist))', pure_link).group()
    spotify_item_url = f'spotify:{item_type}:{spotify_code}'

    return spotify_item_url


def convert_item_spotify_url_to_link(item_spotify_url: str) -> str:
    pattern_match = SPOTIFY_ITEM_URL_PATTERN.match(item_spotify_url)
    assert pattern_match, 'Item Spotify URL seems invalid'

    spotify_code = re.search('\w+$', item_spotify_url).group(0)
    item_type = re.search('((album)|(playlist)|(track)|(artist))', item_spotify_url).group()
    item_link = f'https://open.spotify.com/{item_type}/{spotify_code}'

    return item_link
