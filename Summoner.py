import os
class Summoner:
    def __init__(self, summoner_name: str, summoner_puuid: str, summoner_id: str):
        self.name = summoner_name
        self.puuid = summoner_puuid
        self.id = summoner_id
        self.directory = ''

    def setDirectory(self, dir: str):
        self.directory = dir

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def newSummonerDir(self, dir: str):
        if(not os.path.isDir(dir)):
            return
        else:
            self.setDirectory(dir)
            os.mkdir(dir)
