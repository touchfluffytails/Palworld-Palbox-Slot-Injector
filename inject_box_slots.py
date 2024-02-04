import sys
import json
import os
import configparser
import glob
from datetime import datetime
import shutil
import argparse
import subprocess
import sys
import traceback
import copy

import injector_ui as injectorui

CONFIG_FILENAME = "config.ini"
BLANK_SLOT_FILENAME = "blankpalslot.json"
BACKUP_NAME = "Level_backup-{time}.sav.json"
BACKUP_TIME_FORMAT = "%Y-%m-%d_%H.%M.%S"

ConfigSection = "DEFAULT"
PlayerFolder = "Players"
OpenUi = False

PythonPath = sys.executable
if (PythonPath == None or PythonPath == "" or not os.path.exists(PythonPath)):
    # just default to python command in this case. If this doesn't work, I'm going to assume the user has some weird setup (likely linux) and I'm not providing support
    PythonPath = "python"

def main():
    print("")

    parser = argparse.ArgumentParser(
        prog="Palbox Slot Injector",
        description="Injects slots into existing players palbox")
    parser.add_argument("-l", "--level", metavar="Level.sav[.json]", help="Level.sav[.json] path")
    parser.add_argument("-st", "--savetools", metavar="Save tools cmd", help="convert.cmd path")
    parser.add_argument("-bc", "--boxcount", metavar="Box Count", help="Box count. Ignored if Box slot count not also passed", type=int)
    parser.add_argument("-bsc", "--boxslotcount", metavar="Box Slot Count", help="Box slot count. Ignored if Box count not also passed", type=int)
    parser.add_argument("-ui",  action="store_true", help="Open ui popups. Doesn't prompt for values passed except if you don't pass both box count and box slot count")
    parser.add_argument("-ddp", "--dontdumpplayers",  action="store_true", help="Don't dump player .json")
    args = parser.parse_args()

    openUi = args.ui
    global OpenUi
    OpenUi = openUi
    levelSavePath = args.level
    savetools = args.savetools
    passedBoxCount = args.boxcount
    passedBoxSlotCount = args.boxslotcount
    dumpPlayers = not args.dontdumpplayers

    #default game values
    boxCount = 30
    boxSlotCount = 30

    if (not ValidateArguments(args)):
        print("Exiting, must pass all required arguments")
        quit()

    if (OpenUi):
        print("Running ui mode")
        levelSavePath, savetools, boxCount, boxSlotCount = HandleSetupUI(levelSavePath, savetools, passedBoxCount, passedBoxSlotCount)
    else:
        print("Running console mode")
        boxCount = passedBoxCount
        boxSlotCount = passedBoxSlotCount

    print("Level Save Path: {path}".format(path=levelSavePath))
    print("Save-Tools Path: {path}".format(path=savetools))
    print("Box Count: {value}".format(value=boxCount))
    print("Box Slot Count: {value}".format(value=boxSlotCount))

    savetoolsName, savetoolsExtension = os.path.splitext(savetools)
    if (savetoolsExtension.upper() == ".cmd".upper()):
        print("Assuming save-tools .py is same name as .cmd")
        savetools = savetoolsName + ".py"
    elif (savetoolsExtension.upper() != ".py".upper()):
        print("What king of file are you passing for savetools? Needs to be the .cmd or .py file")
        print("Passed along this for savetools: {path}".format(savetools))
        quit()

    if (not os.path.exists(levelSavePath)):
        print("Level.sav[.json] doesn't exist: {path}".format(path=levelSavePath))
        quit()

    levelName, levelExtension = os.path.splitext(levelSavePath)

    if (levelExtension.upper() not in [".sav".upper(), ".json".upper()]):
        print("Not passed a valid file. Must be a *.sav or *.sav.json")
        print("Was passed file: {path}".format(path=levelSavePath))
        quit()

    levelSavePath = HandleSaveTools(savetools, levelSavePath, dumpPlayers)

    print("Working on Level.sav.json from: {path}".format(path=levelSavePath))

    runningPath = os.path.dirname(os.path.realpath(__file__))
    print("Opened script at: {path}".format(path=runningPath))

    print("Configured Pal box count: {count}".format(count=boxCount))
    print("Configured Pal box slot count: {count}".format(count=boxSlotCount))

    InjectBoxes(levelSavePath, boxCount, boxSlotCount, runningPath)

    result = False
    if (OpenUi):
        result = injectorui.MessageBox.ShowDialog("Merge changes to level.sav", "Do you want to merge changes back into Level.sav made in Level.sav.json?")
    else:
        result = HandleYesNoConsole("Do you want to merge changes back into Level.sav made in Level.sav.json?")
    if (result):
        print("Merging changes back into Level.sav")
        RunSaveTools(savetools, levelSavePath, False)
    else:
        print("Not merging changes back into Level.sav")


def InjectBoxes(levelSavePath, boxcount, boxSlotCount, runningPath):
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
    idiot = False
    idiotAnswered = False
    for container in levelPalBoxes:
        palbox = container["value"]["Slots"]["value"]["values"]
        if (desiredSlotCount < len(palbox)):
            idiot, idiotAnswered = MurderPalBox(container, palbox, desiredSlotCount, idiotAnswered, idiot)
        else:
            playerBlankSlots = copy.deepcopy(blankSlot)
            tribeId = palbox[0]["PermissionTribeID"]["value"]["value"]
            playerBlankSlots["PermissionTribeID"]["value"]["value"] = tribeId
            while (len(palbox) < desiredSlotCount):
                palbox.append(playerBlankSlots)

    print("Backing up previous level.sav.json...")
    currentTime = datetime.now().strftime(BACKUP_TIME_FORMAT)
    saveBackupName = BACKUP_NAME.format(time=currentTime)
    newPath = os.path.join(saveFolder, saveBackupName)
    shutil.move(levelSavePath, newPath)
    
    print("Dumping new level.sav.json...")
    with open(levelSavePath, "w", encoding="utf-8") as file:
        json.dump(levelSave, file)

    print("")
    if (idiot or idiotAnswered):
        print("Pal box slots mutated {count} player pal boxes".format(count=len(playerSaves)))
        print("Remember to ensure your save is correct after removing slots")
    else:
        print("Pal box slots injected into {count} player pal boxes".format(count=len(playerSaves)))
    print("")

def MurderPalBox(container, palbox, desiredSlotCount, idiotAnswered, idiot):
    result = False
    guid = container["key"]["ID"]["value"]
    if (not idiot):
        if (OpenUi):
            result = injectorui.MessageBox.ShowDialog("Reducing box size", "You are asking to reduce box of size {boxsize} down to size {newsize}. Are you SURE you want to do this? This will delete the contents of the reduced slots.".format(boxsize=len(palbox), newsize=desiredSlotCount))
            if (result):
                result = injectorui.MessageBox.ShowDialog("Reducing box size", "Are you truly sure about this? The reduced slots data will not be recoverable if there is no backups.")
            if (result and not idiotAnswered):
                idiot = injectorui.MessageBox.ShowDialog("Apply to all players", "Do you want to apply this to all player boxes?")
                idiotAnswered = True
        else:
            result = HandleYesNoConsole("You are asking to reduce box of size {boxsize} down to size {newsize}. Are you SURE you want to do this?\nThis will delete the contents of the reduced slots.".format(boxsize=len(palbox), newsize=desiredSlotCount))
            if (result and not idiotAnswered):
                idiot = HandleYesNoConsole("Do you want to apply this to all player boxes?")
    else:
        result = True
    if (result):
        print("Reducing palbox size from {boxsize} to {newsize}".format(boxsize=len(palbox), newsize=desiredSlotCount))
        # Lazy, so just while loop it in-reference
        while (len(palbox) > desiredSlotCount):
            del(palbox[-1])
        print("Palbox is now size {newsize}".format(newsize=len(palbox)))
        print("You will have to clean up all pal references contained in guid {guid} that were over slot {size} yourself.".format(guid=guid, size=len(palbox)))
        print("The game will likely crash or otherwise have other issues if you don't clean up dangling slots.")
    else:
        print("Skipping reducing box size")

    return idiot, idiotAnswered

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

def ValidateArguments(args):
    if (args.ui):
        # Literally doesn't matter in this case
        # If its been passed we'll use it and validate otherwise we will prompt
        return True

    if (args.level == None or args.level == ""):
        print("Running without ui, must pass level path")
        return False
    if (args.savetools == None or args.savetools == ""):
        print("Running without ui, must pass savetools path")
        return False
    if (args.boxcount == None or args.boxcount == ""):
        print("Running without ui, must pass box count")
        return False
    if (args.boxslotcount == None or args.boxslotcount == ""):
        print("Running without ui, must pass box slot count")
        return False

    return True

def HandleSetupUI(levelSavePath, savetools, passedBoxCount, passedBoxSlotCount):
    boxCount = 0
    boxSlotCount = 0

    if (levelSavePath == None or levelSavePath == "" or not os.path.exists(levelSavePath)):
        levelFileDialog = injectorui.LevelFileDialog()
        levelSavePath = levelFileDialog.GetPath()
        if (levelSavePath == None or levelSavePath == "" or levelSavePath == False):
            print("")
            print("You must select a level save path")
            print("")
            raise Exception("User did not select a level save")

    if (savetools == None or savetools == "" or not os.path.exists(savetools)):
        savetoolsFileDialog = injectorui.SaveToolsCmd()
        savetools = savetoolsFileDialog.GetPath()
        if (savetools == None or savetools == "" or savetools == False):
            print("")
            print("You must select savetools path")
            print("")
            raise Exception("User did not select savetools path")

    if (passedBoxCount == None or passedBoxCount == 0 or passedBoxSlotCount == None or passedBoxSlotCount == 0):
        settingInput = injectorui.SettingsInput()
        settingInput.OpenDialog()
        boxCount = settingInput.GetBoxCount()
        boxSlotCount = settingInput.GetBoxSlotCount()
        if (boxCount == None or boxCount == 0 or boxCount == False or boxSlotCount == None or boxSlotCount == 0 or boxSlotCount == False):
                print("")
                print("You must provid a valid positive number for both box slot and box slot count")
                if (boxCount != None and boxCount != 0 and boxCount != False):
                    print("Box count set: {value}".format(value=boxCount))
                if (boxSlotCount != None and boxSlotCount != 0 and boxSlotCount != False):
                    print("Box slot count set: {value}".format(value=boxSlotCount))
                print("")
                raise Exception("User did not input valid box setting values")

    return levelSavePath, savetools, boxCount, boxSlotCount

def RunSaveTools(savetools, savePath, validateJsonExistence = True):
    saveName, saveExtension = os.path.splitext(savePath)

    returnPath = ""
    if (saveExtension.upper() == ".sav".upper()):
        returnPath = savePath + ".json"
    elif (saveExtension.upper() == ".json".upper()):
        saveName, saveExtension = os.path.splitext(saveName)
        if (saveExtension.upper() != ".sav".upper()):
            print("Your json file doesn't have a .sav suffix. What are you doing?")
            print("Tried dealing with the json file: {path}".format(path=savePath))
            raise Exception("Your .json file needs to end in .sav.json.")
        returnPath = saveName + saveExtension

    if (validateJsonExistence and saveExtension.upper() == ".sav".upper()):
        jsonPath = savePath + ".json"
        if (os.path.exists(jsonPath)):
            result = False
            if (OpenUi):
                result = injectorui.MessageBox.ShowDialog("Level already dumped", "Level.sav.json already exists.\nDo you still want to run save-tools on the level save?\n\nUnless you know what you are doing, this is normally Yes.")
            else:
                result = HandleYesNoConsole("Do you still want to run save-tools on the level save?")
            if (not result):
                print("User skipped dumping level.sav")
                print("")
                return jsonPath

    print("Running save-tools on {path}".format(path=savePath))
    print("")
    result = subprocess.run([PythonPath, savetools, savePath, "--force"])
    print("")
    if (result.returncode == 1):
        print("Error while running save-tools on {path}".format(path=savePath))
        print("")
        raise Exception("Failure running save-tools")

    return returnPath

def HandleYesNoConsole(message):
    result = ""
    while (result.upper() not in ["y".upper(), "n".upper()]):
        result = input(message + " (y/n): ")
    if (result.upper() == "y".upper()):
        return True
    else:
        return False

def DumpLevelSave(savetools, levelSavePath):
    return RunSaveTools(savetools, levelSavePath)

def DumpPlayerSaves(savetools, levelSavePath):
    saveFolder = os.path.split(levelSavePath)[0]
    playersFolder = os.path.join(saveFolder, PlayerFolder)

    playerSaves = []

    for file in glob.glob(os.path.join(playersFolder, "*.sav")):
        playerSaves.append(file)

    for save in playerSaves:
        RunSaveTools(savetools, save, False)

def HandleSaveTools(savetools, levelSavePath, dumpPlayers):
    levelName, levelExtension = os.path.splitext(levelSavePath)
    savePath = levelSavePath
    if (levelExtension.upper() == ".sav".upper()):
        print("Dumping level.sav...")
        savePath = DumpLevelSave(savetools, levelSavePath)

    if (dumpPlayers):
        print("Dumping player saves...")
        DumpPlayerSaves(savetools, levelSavePath)

    return savePath

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
        print(traceback.print_exception(type(ex), ex, ex.__traceback__))

