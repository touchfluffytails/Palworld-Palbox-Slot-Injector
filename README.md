# Palworld-Palbox-Slot-Injector
Injects slots into existing players palboxes. Allows you to increase the amount of possible slots you can have in the boxes. It does not, however, allow you to access those slots without a mod.

Works alongside a mod like: https://www.nexusmods.com/palworld/mods/68  
You can edit the main.lua script this mod comes with to edit the box count and slot sizes  

Game appears to work by having slots be an ordered array containing box slots in a contiguous order. How many slots you have is based on box count * slots per box. Based on these parameters, you can just inject new slots to the save based on your desired box count and slots per boxes setup in a mod like the previously listed.  

**Tools needed:**  
Python installed  
Palworld-Save-Tools: https://github.com/cheahjs/palworld-save-tools/  

**How to use:**  
1. Run "Palworld-Save-Tools" against "Level.sav" to get "Level.sav.json" in the directory  
2. In save "Players" folder, run "Palworld-Save-Tools" against all player .sav so that you have x.sav.json  
- eg. "00000000000000000000000000000001.sav" -> "00000000000000000000000000000001.sav.json"  
3. In "config.ini" in script folder, modify "boxcount" number to desired box number and "boxslotcount" to desired slots per box  
4. Drag your "Level.sav.json" onto the "inject_box_slots.cmd" or command line it  
- Must be "**Level.sav.json**" not "Level.sav"  
5. Install a mod like previously stated "Bigger and Reorganized PalBox" to allow displaying of the new box slots  

It will automatically read player .sav.json's in the Players folder to find their palbox guid and inject box slots to the required amount  

**Notes:**  
I am unaware of what possible issues this could cause so use with caution and awareness this may break something and be irreversible. It already backups level.sav.json but be sure to do it yourself.  
