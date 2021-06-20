import os
from os import system
import requests
import json
import time
import os.path
from os import path
from dotenv import load_dotenv
import math

#urls 
KEY = '?api_key=' + os.getenv('RIOT_KEY')
KEY_APPENDED = '&api_key=' + os.getenv('RIOT_KEY')
base_url = 'https://na1.api.riotgames.com'

base_regions_url = 'https://americas.api.riotgames.com'
summoner_request_url = '/lol/summoner/v4/summoners/by-name/'
summoner_matches_url ='/lol/match/v5/matches/by-puuid/'

summoner_puuid_url = '/lol/summoner/v4/summoners/by-puuid/'

matches_url = '/lol/match/v5/matches/'

matches_url_append = '/ids?start=0&count='
number_of_matches = 10

gamemode_dictionary = {}

def getMostRecentMatch(summoner_name: str):
    
    start_time = time.time()
    request = requests.get(base_url + summoner_request_url + summoner_name + KEY)
    if request.status_code != 200:
        print('Summoner Not Found!')
        print("Status Code: " + str(request.status_code))
        exit(2)

    summoner_json = request.json()

    summoner_puuid = summoner_json['puuid']
    request = requests.get(base_regions_url + summoner_matches_url + summoner_puuid + matches_url_append + str(number_of_matches) + KEY_APPENDED)
    if request.status_code != 200:
        print('Error!')
        print("Status Code: " + str(request.status_code))
        exit(3)
    match_json = request.json()
    

    if len(match_json) == 0:
        print('No Matches Found')
        os._exit(4)
    match_list = []
    for match in match_json:
        match_list.append(match)
    
    last_match_json = getMatchJson(match_list, summoner_puuid)

    game_start_time = last_match_json['info']['gameCreation'] // 1000

    time_since_game = getTimeSinceGame(start_time, game_start_time)
    print('\nPlayed ' + time_since_game)
    #in seconds
    game_duration = last_match_json['info']['participants'][0]['timePlayed']
    duration_str = ''
    hours = game_duration // 3600
    minutes_decimal = (game_duration / 60) % 60
    minutes =  (game_duration // 60) % 60
    seconds = game_duration % 60
    if game_duration > 3600 :
        
        duration_str = '%02d:%02d:%02d' % (hours, minutes, seconds)
    else:
        duration_str = '%02d:%02d' % (minutes, seconds)
    
    mode = getGameMode(last_match_json['info']['queueId'])
    print('\nGamemode: ' + mode)
    print('Game Duration: ' + duration_str)


    participant_list = getParticipants(last_match_json['info']['participants'])
    participant_kda = getKDA(last_match_json)
    print('\n%-27s\t%-27s\n' % ('Red Team', 'Blue Team'))
    for i in range(len(participant_list) // 2):
        blue_index = i + (len(participant_list) // 2)
        print('%-16s %-10s\t%-16s %-10s' % (participant_list[i], participant_kda[i], 
            participant_list[blue_index], participant_kda[blue_index]))
    end_time = time.time()

    
    print('\nTime Elapsed: ' + str(math.trunc((end_time - start_time) * 1000)) + ' ms\n')
def getMatchJson(match_ids: list, summoner_puuid: str):
    for match_id in match_ids:
        file_path = 'matches/' + match_id + '.json'

        if (os.path.exists(file_path)):
            data = {}
            with open(file_path) as f:
                data = json.load(f)
            return data
        else:
            #get request
            request = requests.get(base_regions_url + matches_url + match_id + KEY)
            if request.status_code == 200:
                match_json = request.json()
                
                with open(file_path, 'w') as json_file:
                    json.dump(match_json, json_file)
                return match_json
    return None

def getParticipants(participant_list: list):
    '''Takes a list of id's and returns a list of corresponding summoner names'''
    summoner_list = []
    for participant in participant_list:
        
        
        summoner_list.append(participant['summonerName'])
    return summoner_list

def getTimeSinceGame(current: int, game_time: int):
    time_since = current - game_time
    seconds = int(time_since % 60)
    minutes = int((time_since // 60) % 60)
    hours = int((time_since // 3600) % 24)
    days = int((time_since // 86400) % 365)
    years = int((time_since // 31536000))
    if years > 0:
        if years == 1:
            return 'a year ago'
        return str(years) + ' years ago'
    elif days > 0:
        if days == 1:
            return 'a day ago'
        return str(days) + ' days ago'
    elif hours > 0:
        if hours == 1:
            return 'an hour ago'
        return str(hours) + ' hours ago'
    elif minutes > 0:
        if minutes == 1:
            return 'a minute ago'
        return str(minutes) + ' minutes ago'
    else:
        if seconds == 1:
            return 'a second ago'
        return str(seconds) + ' seconds ago'

def getKDA(match_json: dict):
    '''Takes dictionary json of the map and returns a list of KDA'''
    kda_list = []
    for participant in match_json['info']['participants']:
        kills = participant['kills']
        deaths = participant['deaths']
        assists = participant['assists']
        kda_list.append(str(kills) + '/' + str(deaths)+ '/' + str(assists))
    return kda_list

def getCSMin(match_json: dict, min: float):
    '''Takes dictionary json of the map and returns a list of cs/min values'''
    cs_list = []
    for participant in match_json['info']['participants']:
        cs = participant['totalMinionsKilled']
        cs_list.append(cs / min)
    return cs_list

def getGameMode(game_id: int):
    if (game_id in gamemode_dictionary):
        return gamemode_dictionary[game_id]
    else:
        return 'Special Gamemode'

def populateGamemodeDict():
    gamemode_dictionary[400] = "Draft Pick"
    gamemode_dictionary[430] = 'Blind Pick'
    gamemode_dictionary[420] = 'Ranked Solo'
    gamemode_dictionary[440] = 'Ranked Flex'
    gamemode_dictionary[450] = 'ARAM'
    gamemode_dictionary[700] = 'Clash'
    gamemode_dictionary[1300] = 'Nexus Blitz'



#driver
system('clear')
populateGamemodeDict()
name = input('Summoner Name: ')
getMostRecentMatch(name)