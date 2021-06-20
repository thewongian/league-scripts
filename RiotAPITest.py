import os
from os import system, name
import requests
import json
from dotenv import load_dotenv



mastery_request_url = '/lol/champion-mastery/v4/champion-masteries/by-summoner/'

KEY = '?api_key=' + os.getenv('RIOT_KEY')

base_url = 'https://na1.api.riotgames.com'

summoner_request_url = '/lol/summoner/v4/summoners/by-name/'

cdragon_champion_url = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/'


def getChampionJson(id: int):
    '''Takes Champion ID and returns Champion JSON'''
    request = requests.get(cdragon_champion_url + str(id) + '.json')

    return request.json()
_ = system('clear')
summoner_name = input('Summoner Name: ')

request = requests.get(base_url + summoner_request_url + summoner_name + KEY)

if request.status_code != 200:
    print('Summoner not found!')
    print('Status Code: ' + str(request.status_code))
    exit

summoner_json = request.json()
summoner_id = summoner_json['id']
request = requests.get(base_url + mastery_request_url + summoner_id + KEY)
mastery_json = request.json()

champion1_json = getChampionJson(mastery_json[0]['championId'])
champion2_json = getChampionJson(mastery_json[1]['championId'])
champion3_json = getChampionJson(mastery_json[2]['championId'])
print(summoner_json['name']+ '\'s Top Champions')
print('Mastery Level ' + str(mastery_json[0]['championLevel']) + ' ' + champion1_json['name'] + ': ' + str(mastery_json[0]['championPoints']) + ' Mastery Points')
print('Mastery Level ' + str(mastery_json[1]['championLevel']) + ' ' + champion2_json['name'] + ': ' + str(mastery_json[1]['championPoints']) + ' Mastery Points')
print('Mastery Level ' + str(mastery_json[2]['championLevel']) + ' ' + champion3_json['name'] + ': ' + str(mastery_json[2]['championPoints']) + ' Mastery Points')

