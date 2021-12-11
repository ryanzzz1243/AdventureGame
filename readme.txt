All code by Ryan Edwards rje7hp
IT 4401 taught by Dale Musser
10 December 2021

This is an adventure game. The game fulfills a limited but (in my opinion) acceptable scope for what I can finish in the time given.
The game is like a (crappy) hack-n-slash that takes inspiration from Diablo-style games.
The player has a name, species, weapon, armor, and is located somewhere. They can fight creatures in this place or go somewhere else.
Creatures drop gold and occasionally better loot which the player can choose to equip.
In towns, the player can freely heal and trade for better loot.
Players, locations, weapons, armors, and creatures are specified in their files and loaded on game startup.

When you are in any menu (lists 1, 2, 3, etc), pressing Ctrl-C (KeyboardInterrupt) will exit that menu, instead of the whole game.
Protip: You can heal in the market.

Running the code in IDLE works, but I developed this entirely in VS Code which uses Powershell.
To start it in Powershell and see the fancy text clearing, hold shift and right click the folder (rje7hp_final) -> Open in Powershell, then run driver.py with Python3 
(for me this is "py driver.py" but could be "python driver.py" or "python3 driver.py" depending on install)
Or just get VSCode, which I could not have done this without.