import sys
import json
import os
import configparser
import glob
from datetime import datetime
import shutil
import argparse

CONFIG_FILENAME = "config.ini"
BLANK_SLOT_FILENAME = "blankpalslot.json"
BACKUP_NAME = "Level_backup-{time}.sav.json"
BACKUP_TIME_FORMAT = "%Y-%m-%d_%H.%M.%S"

ConfigSection = "DEFAULT"
PlayerFolder = "Players"

def main(levelSavePath, boxcount, boxSlotCount, runningPath):
    saveFolder = os.path.split(levelSavePath)[0]
    playersFolder = os.path.join(saveFolder, PlayerFolder)

    desiredSlotCount = boxcount * boxSlotCount
    print("Desired total slot count is: {count}".format(count=desiredSlotCount))

    print("Getting player saves...")
    playerSaves = []
    for file in glob.glob(os.path.join(playersFolder, "*.json")):
        playerSaves.append(file)
    print("{count} players with json dumped for this world".format(count=len(playerSaves)))
    if (len(playerSaves) == 0):
        print("No player .sav.json found to inject slots into")
        print("{count} player saves found that haven't been dumped with the save tool".format(count=GetPlayerSaveCount(playersFolder)))
        quit()

    print("Getting player pal boxes...")
    playerPalBoxes = []
    for player in playerSaves:
        save = {}
        with open(player, "r", encoding="utf-8") as file:
            save = json.load(file)
            containerId = save["properties"]["SaveData"]["value"]["PalStorageContainerId"]["value"]["ID"]["value"]
            playerPalBoxes.append(containerId)

    print("Getting blank slot template...")
    blankSlot = {}
    blankPath = os.path.join(runningPath, BLANK_SLOT_FILENAME)
    with open(blankPath, "r", encoding="utf-8") as file:
        blankSlot = json.load(file)
    print("Loaded following file as blank slot template: {path}".format(path=blankPath))

    print("Loading level save...")
    levelSave = {}
    with open(levelSavePath, "r", encoding="utf-8") as file:
        levelSave = json.load(file)
    levelContainers = levelSave["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"]

    print("Getting all known player pal box structures...")
    levelPalBoxes = []
    for container in levelContainers:
        if (container["key"]["ID"]["value"] in playerPalBoxes):
            levelPalBoxes.append(container)

    print("Injecting blank slots to player pal boxes to size {size}...".format(size=desiredSlotCount))
    for container in levelPalBoxes:
        palbox = container["value"]["Slots"]["value"]["values"]
        while (len(palbox) < desiredSlotCount):
            palbox.append(blankSlot)

    print("Backing up previous level.sav.json...")
    currentTime = datetime.now().strftime(BACKUP_TIME_FORMAT)
    saveBackupName = BACKUP_NAME.format(time=currentTime)
    newPath = os.path.join(saveFolder, saveBackupName)
    shutil.move(levelSavePath, newPath)
    
    print("Dumping new level.sav.json...")
    with open(levelSavePath, "w", encoding="utf-8") as file:
        json.dump(levelSave, file)

    print("")
    print("Pal box slots injected into {count} player pal boxes".format(count=len(playerSaves)))

def GetPlayerSaveCount(playersFolder):
    playerSaves = glob.glob(os.path.join(playersFolder, "*.sav"))
    return len(playerSaves)

def CreateDefaultConfig(configPath):
    config = configparser.ConfigParser()
    config.read(configPath)
    # default game values
    config.set(ConfigSection, "boxcount", "16")
    config.set(ConfigSection, "boxslotcount", "30")
    with open(configPath, 'w', encoding="utf-8") as file:
        config.write(file)

if __name__ == "__main__":
    print("")

    parser = argparse.ArgumentParser(
        prog="Palbox Slot Injector",
        description="Injects slots into existing players palbox")
    parser.add_argument("level", metavar="Level.sav.json")
    args = parser.parse_args()

    levelSavePath = args.level

    if (not os.path.exists(levelSavePath)):
        print("Level.sav.json doesn't exist: {path}".format(path=levelSavePath))
        quit()

    levelName, levelExtension = os.path.splitext(levelSavePath)
    if (levelExtension.upper() == ".sav".upper()):
        print("Must be passed Level.sav.json, not Level.sav")
        print("Please ensure you have ran Level.sav through Palword-Save-Tools")
        print("Was passed file: {path}".format(path=levelSavePath))
        quit()
    elif (levelExtension.upper() != ".json".upper()):
        print("Not passed a valid file")
        print("Was passed file: {path}".format(path=levelSavePath))
        quit()

    print("Working on Level.sav.json from: {path}".format(path=levelSavePath))

    runningPath = os.path.dirname(os.path.realpath(__file__))
    print("Opened script at: {path}".format(path=runningPath))

    configPath = os.path.join(runningPath, CONFIG_FILENAME)
    if (not os.path.exists(configPath)):
        CreateDefaultConfig(configPath)
        print("{config} did not exist. Created, please edit".format(config=configPath))
        quit()

    config = configparser.ConfigParser()
    config.read(configPath)
    boxCount = config.getint(ConfigSection, "boxcount")
    boxSlotCount = config.getint(ConfigSection, "boxslotcount")

    print("Configured Pal box count: {count}".format(count=boxCount))
    print("Configured Pal box slot count: {count}".format(count=boxSlotCount))

    main(levelSavePath, boxCount, boxSlotCount, runningPath)
