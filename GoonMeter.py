import os
from os import system
import requests
import json
import time

from dotenv import load_dotenv

#urls 
KEY = '?api_key=' + os.getenv('RIOT_KEY')
KEY_APPENDED = '&api_key=' + os.getenv('RIOT_KEY')
base_url = 'https://na1.api.riotgames.com'

base_regions_url = 'https://americas.api.riotgames.com'
summoner_request_url = '/lol/summoner/v4/summoners/by-name/'
summoner_matches_url ='/lol/match/v5/matches/by-puuid/'

matches_url = '/lol/match/v5/matches/'

matches_url_append = '/ids?start=0&count='

number_of_matches = 100
DEFAULT_TIMEOUT_TIME = 2
#Methods
def getGoonDictionary():
    '''Returns Goon Values Dictionary by Champion'''
    goon_dictionary = {}
    with open('goon_values.json') as goon_values:
        goon_dictionary = json.load(goon_values)
    return goon_dictionary
def getMostPlayedChamp(champs: list):
    '''Returns most played champion in the list'''
    champ_map = {}
    for champ in champs:
        if champ not in champ_map:
            champ_map[champ] = 1
        else:
            champ_map[champ] += 1

    most_played = ""
    current_max = 0
    for champ in champ_map:
        if champ_map[champ] > current_max:
            current_max = champ_map[champ]
            most_played = champ
    request = requests.get('http://ddragon.leagueoflegends.com/cdn/11.11.1/data/en_US/champion/' + most_played + '.json')
    if request.status_code == 200:
        champ_json = request.json()
        print('\nMost Played Champion: ' + champ_json['data'][most_played]['name'] + ' (' + str(champ_map[most_played]) + ' Games)')

def getMatchChampion(match_id:str, summoner_puuid: str):
    '''Get champion used in a match'''
    request = requests.get(base_regions_url + matches_url + match_id + KEY)
    if request.status_code == 404:
        return None
    elif request.status_code == 429:
        time.sleep(DEFAULT_TIMEOUT_TIME)
        return None
    elif request.status_code != 200:
        print(base_regions_url + matches_url + match_id + KEY)
        print('Error!')
        print('Status Code: ' + str(request.status_code))
        exit(1)
    match_json = request.json()
    summoner_index = 0
    for count, id in enumerate(match_json['metadata']['participants']):
        if id == summoner_puuid:
            summoner_index = count
            break

    return match_json['info']['participants'][summoner_index]['championName']

def getGoonScore(summonerName: str):
    '''Returns a float that represents average goon score'''
    start_time = time.time()
    print('\nCalculating Goon Score...\n')
    goon_dic = getGoonDictionary()
    champ_list = []

    request = requests.get(base_url + summoner_request_url + summonerName + KEY)
    if request.status_code != 200:
        print('Summoner Not Found!')
        print("Status Code: " + request.status_code)
        exit(2)
    summoner_json = request.json()

    summoner_puuid = summoner_json['puuid']
    summoner_id = summoner_json['id']
    request = requests.get(base_regions_url + summoner_matches_url + summoner_puuid + matches_url_append + str(number_of_matches) + KEY_APPENDED)
    if request.status_code != 200:
        print('Error!')
        print("Status Code: " + str(request.status_code))
        exit(3)
    match_json = request.json()
    
    if len(match_json) == 0:
        print('No Matches Found')
        os._exit(4)
    total = 0
    not_found_count = 0
    for count, match in enumerate(match_json):
        champ = getMatchChampion(match, summoner_puuid)
        if champ == None:
            not_found_count += 1
        else:
            total += goon_dic[champ]
            champ_list.append(champ)
        if count % 20 == 0 and count != 0:
            time.sleep(.5)
        if count == number_of_matches / 2:
            print('\nAnalyzing the last ' + str(number_of_matches) + ' matches...\n')
        
    end_time = time.time()
    print('Done! Time Elapsed: ' + str(int(1000 * (end_time - start_time))) + 'ms')
    getMostPlayedChamp(champ_list)
    
    return float(total) / float(len(match_json) - not_found_count)

def printLast10Champs(summonerName: str):
    '''Prints the last 10 champs played by specified summoner'''
    
    request = requests.get(base_url + summoner_request_url + summonerName + KEY)
    if request.status_code != 200:
        print('Summoner Not Found!')
        print("Status Code: " + request.status_code)
        exit(2)

    summoner_json = request.json()

    summoner_puuid = summoner_json['puuid']
    request = requests.get(base_regions_url + summoner_matches_url + summoner_puuid + matches_url_append + str(number_of_matches) + KEY_APPENDED)
    if request.status_code != 200:
        print('Error!')
        print("Status Code: " + str(request.status_code))
        exit(3)
    match_json = request.json()

    for match in match_json:
 
        print(getMatchChampion(match, summoner_puuid))
        time.sleep(.2)



#Driver Code

system('clear')
print('How Goon Are You?')
summoner_name = input('Summoner Name: ')

request = requests.get(base_url + summoner_request_url + summoner_name + KEY)
if request.status_code != 200:
    print('Summoner Not Found!')
    print("Status Code: " + str(request.status_code))
    exit(2)
summoner_json = request.json()
summoner = summoner_json['name']
print('%s is %.2f%s goon\n' %(summoner, getGoonScore(summoner_name) * 10, '%'))


