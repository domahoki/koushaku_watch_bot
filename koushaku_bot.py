
# -*- encoding: utf-8 -*-

from riotwatcher import RiotWatcher
import discord
import asyncio
from requests import HTTPError
from enum import Enum
import random
import yaml
import sys


SUMM_ID = "6184085"
SUMM_NM = "こうしゃく"
REGION  = "jp1"
GOBI    = "だねぇ～。"
HELP_MSG = "USAGE:\n" \
           "--------------------------------\n" \
           "ランク監視: -l, --lol\n" \
           "配信視聴者監視(未実装): -t, --twitch\n" \
           "ダイスロール: -r, --roll ?d?\n" \
           "ヘルプ: -h, --help\n" \
           "APIキー更新: --set_api_key %API_KEY\n" \
           "--------------------------------"

try:
    yaml_f = open("setting.yaml", "r+")
    yaml_data = yaml.load(yaml_f)
    RIOT_API_KEY = yaml_data("riot_api_key")
    TWITCH_CLIENT_ID = yaml_data("twitch_client_id")
    TOKEN   = yaml_data("discord_token")
except BaseException as err:
    print("Failed to import setting.yaml")
    sys.exit()

class Mode(Enum):
    NONE   = -1
    HELP   = 0
    LOL    = 1
    TWITCH = 2
    DICE   = 3
    API    = 99

global watcher

client = discord.Client()

def find_koushaku_message(message):
    if message.content.startswith("!koushaku"):
        commands = message.content.split(" ")
        for command in commands:
            if command == "-h" or command == "--help":
                return Mode.HELP
            elif command == "-l" or command == "--lol":
                return Mode.LOL
            elif command == "-t" or command == "--twitch":
                return Mode.TWITCH
            elif command == "-r" or command == "--roll":
                return Mode.DICE
            elif command == "--set_api_key":
                return Mode.API
        return Mode.HELP
    return Mode.NONE

def show_lol_stats():
    global watcher
    try:
        koushaku = watcher.league.by_summoner(REGION, SUMM_ID)
        tier = koushaku[0]["tier"]
        for player in koushaku[0]["entries"]:
            if player["playerOrTeamId"] == SUMM_ID:
                koushaku = player
                break
        rank = koushaku["rank"]
        streak = ""
        lp = str(koushaku["leaguePoints"]) + "LP"
        if koushaku["hotStreak"]:
            streak = "\n連勝しているねぇ～！"
        return "今のこうしゃくさんのランクは" + tier + " " + rank + " : " + lp + GOBI + streak
    except HTTPError as _:
        return "APIキーが失効しているねぇ～"

def set_api_key(message):
    global watcher
    RIOT_API_KEY = message.content.split(" ")[2]
    watcher = RiotWatcher(RIOT_API_KEY)

def show_twitch_view_num():
    twitch_client = TwitchClient(client_id=TWITCH_CLIENT_ID)

def dice_roll(message):
    try:
        dice = message.content.split(" ")[2].split("d")
        dice_type = int(dice[0])
        dice_num = int(dice[1])
        result = ""
        for i in range(dice_num):
            result += str(random.randint(1, dice_type))
            if i < (dice_num - 1):
                result += ", "
        return result
    except BaseException as _:
        return "うまく転がせないよぉ～"

@client.event
async def on_ready():
    global watcher
    watcher = RiotWatcher(RIOT_API_KEY)

@client.event
async def on_message(message):
    mode = find_koushaku_message(message)
    if mode == Mode.LOL:
        lol_msg = show_lol_stats()
        await client.send_message(message.channel, lol_msg)
    elif mode == Mode.API:
        set_api_key(message)
        await client.send_message(message.channel, "APIキーを更新したよぉ～")
    elif mode == Mode.HELP:
        await client.send_message(message.channel, HELP_MSG)
    elif mode == Mode.DICE:
        dice_msg = dice_roll(message)
        await client.send_message(message.channel, dice_msg)

client.run(TOKEN)
