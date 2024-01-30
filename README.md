# Palworld-Palbox-Slot-Injector
Injects slots into existing players palboxes. Allows you to increase the amount of possible slots you can have in the boxes. It does not however allow you to access those slots without a mod.

Works alongside a mod like: https://www.nexusmods.com/palworld/mods/68

Game appears to work by having slots be an ordered array containing box slots in a contiguous order. How many slots you have is based on box count * slots per box. Based on these parameters, you can just inject new slots to the save based on your desired box count and slots per boxes setup in a mod like the previously listed.

Tools needed:
Python installed
Palworld-Save-Tools: https://github.com/cheahjs/palworld-save-tools/

How to use:
Ensure you've already dumped level.sav and and all player savs to json
Set your box count and box slot count in the config.ini
Drag your level.sav.json onto the inject_box_slots.cmd

Notes:
I am unaware of what possible issues this could cause so use with caution and awareness this may break something. It already backups level.sav.json but be sure to do it yourself.
