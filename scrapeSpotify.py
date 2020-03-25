import requests
from jsonmerge import merge
import pandas as pd
from datetime import date

token='BQB6l5lTO0Q2cym2QQ7yfusTsm0X72HpaudWn4T7xz1-IPCvRZy5EiRPLIdbpSe9GbcziroivMfcABDhi0Yy5yuSLTM7UrZ6QYnUTWTVOr3p6r7x9NRCuEDvfaKVP59rmTu-18naHm8rXTA'

def requestToServer(url):
    tokenString = 'Bearer ' + token
    headers = {'Authorization': tokenString}
    req = requests.get(url, headers=headers)
    return req.json()

def getPlaylistData(playlistID):
    url = 'https://api.spotify.com/v1/playlists/' + playlistID + '/tracks?market=ES&fields=items(track(name%2Chref))'
    playlistData = requestToServer(url)
    songIDs = []
    for item in playlistData['items']:
        longid = item['track']['href']
        id = longid[longid.rfind('/')+1:]
        songIDs.append({'title': item['track']['name'], 'id': id})
    return songIDs


def getIDList(songList , type):
    idList = ''
    for song in songList:
        idList = idList + song[type] +','
    return idList[:-1]


def getSongFeatures(songList):
    idList = getIDList(songList, 'id')
    url = 'https://api.spotify.com/v1/audio-features?ids=' + idList
    songInfo = requestToServer(url)['audio_features']
    for i in range(0, len(songList)):
        songList[i] = merge(songList[i], songInfo[i])
    return songList


def getTrackInfo(songList):
    idList = getIDList(songList, 'id')
    url = 'https://api.spotify.com/v1/tracks?ids=' + idList
    songInfo = requestToServer(url)['tracks']
    for i in range(0, len(songList)):
        popInfo = {'popularity': songInfo[i]['popularity']}
        songList[i] = merge(songList[i], popInfo)
        artistInfo = {'artist_name': songInfo[i]['artists'][0]['name'], 'artist_id': songInfo[i]['artists'][0]['id']}
        songList[i] = merge(songList[i], artistInfo)
        albumInfo = {'album_name': songInfo[i]['album']['name'], 'album_id': songInfo[i]['album']['id']}
        songList[i] = merge(songList[i], albumInfo)
        explInfo = {'explicit': songInfo[i]['explicit']}
        songList[i] = merge(songList[i], explInfo)
        trackInfo = {'track_number': songInfo[i]['track_number']}
        songList[i] = merge(songList[i], trackInfo)
    return songList


def getArtistInfo(songList):
    idList = getIDList(songList, 'artist_id')
    url = 'https://api.spotify.com/v1/artists?ids=' + idList
    artistInfo = requestToServer(url)['artists']
    for i in range(0, len(songList)):
        followerInfo ={'artist_followers': artistInfo[i]['followers']['total']}
        songList[i] = merge(songList[i], followerInfo)
        artPop ={'artist_popularity': artistInfo[i]['popularity']}
        songList[i] = merge(songList[i], artPop)
    return songList


def export(playlistID):
    songList = getPlaylistData(playlistID)
    print(songList)
    songList = getSongFeatures(songList)
    size = int(len(songList)/2)
    songListTemp1 = getTrackInfo(songList[0:size])
    songListTemp2 = getTrackInfo(songList[size:])
    songListTemp1 = getArtistInfo(songListTemp1)
    songListTemp2 = getArtistInfo(songListTemp2)

    songList = songListTemp1 + songListTemp2
    df = pd.DataFrame(songList)
    namestr = str(date.today()) + '-' + playlistID[10:]
    with pd.ExcelWriter("C:\\Users\\wlhun\\OneDrive\\Documents\\1-Comp Sci Projects\\DAT121-Paper\\Spotify Scrape.xlsx",
                    mode='a', engine='openpyxl') as writer:
        df.to_excel(writer,  sheet_name=namestr)

def main():
    playlists = ['37i9dQZF1Etc5ssYXmHgzg', '37i9dQZF1EtoVydsGKdS5o', '37i9dQZF1Et8POOJWXmGS1', '7sGjEQr2sgsSlCSlMk3NcA', '7xQOqbKgu1Qmu61tW3uxVo', '37i9dQZF1Ejxj76Bb3DGjr', '37i9dQZF1Eti4lqh5A1srQ', '37i9dQZF1CAsHxDwzYfpaF']
    for playlist in playlists:
        export(playlist)


main()
