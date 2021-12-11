from os import system
from os.path import exists
import fileinput
import random
import math
from typing import ClassVar, Type

clear = lambda: system('cls')

ADJECTIVES_BAD = ("evil", "disgusting", "dirty", "horrible", "awful", "terrible", "menacing", "dastardly", "wicked", "vile", "foul", "vulgar", "rotten", "sick", "vicious", "wretched", "horrid", "nasty", "appalling", "hellish")
ADJECTIVES_GOOD = ("wonderful", "wondrous", "amazing", "awesome", "great", "fantastic", "regal", "marvelous", "lovely", "magnificent", "glorious", "delightful")

PLACES_SLEEPING = ("in a tavern", "in a hostel", "on the street", "in an alleyway", "in a ditch", "in a garbage bin", "on a nice bed", "on a rooftop overlooking the town", "in a cozy place", "in an awfully smelly corner")
PLACES_FIGHT = ("forests", "outlying trade routes", "caves", "labyrinth", "abandoned mineshafts", "woodlands", "rolling hills", "mountains", "firey caves", "highlands")

DAMAGE_TYPE = {"none": -1, "physical": 0, "magic": 1, "true": 2}
DAMAGE_TYPE_INV = {value: key for key, value in DAMAGE_TYPE.items()}
PLAYER_STATUS = {"sleeping": 0, "resting": 1, "travelling": 2, "fighting": 3, "idle": 4}
PLAYER_STATUS_INV = {value: key for key, value in PLAYER_STATUS.items()}
INTERPRET_BOOL = {"no": False, "yes": True}

CSV_DELIM = ","
CSV_TUP_DELIM = "|"

FILE_LOCATIONS = "bin/locations.csv"
FILE_ARMORS = "bin/armors.csv"
FILE_WEAPONS = "bin/weapons.csv"
FILE_CREATURES = "bin/creatures.csv"
FILE_PLAYERS = "bin/players.csv"
FILE_DEFAULT_PLAYERS = "bin/players_default.csv"

def getDefaultGenerator() -> dict:
    with open(FILE_DEFAULT_PLAYERS, 'r') as f:
        aspects = f.readline().strip(",\n").split(CSV_DELIM)
    return {key: None for key in aspects}

# getMenu is reused from my previous submissions
def getMenu(*args: str):
    '''Given a list of strings, generates a menu and returns a valid user input as an int.'''
    counter = 1
    for option in args:
        print(f"{counter}. {option}")
        counter += 1
    try:
        in1 = input("Choose an option: ")
    except KeyboardInterrupt:
        clear()
        print("Cancelled menu!")
        return None
    upper = len(args) + 1
    try:
        if(in1.isdigit()):
            in1 = int(in1)
            if(in1 in range(1, upper)):
                return in1
            else:
                print("Invalid option selection. Please try again.")
                return getMenu(*args)
        else:
            print("Invalid characters detected. Please use only the number representing the option you wish to choose.")
            return getMenu(*args)
    except(ValueError, TypeError):
        print("Invalid input. Please use only the number representing the option you wish to choose.")
        return getMenu(*args)

def getUnusedPlayerName(players: list) -> str:
        '''Check name and return if valid.'''
        name = getValidUserString("What is your name? : ")
        if name:
            for player in players:
                if name == player.name:
                    print(f"{name} is already in use! Specify a unique name.")
                    return getUnusedPlayerName(players)
            return name
        else:
            return None

def getUsedPlayerName(players: list):
        '''Check name and return if valid.'''
        name = getValidUserString("What is your name? : ")
        if name:
            for player in players:
                if name == player.name:
                    print(f"{name} found!")
                    return name
            print("Name not found. Specify a name that has been used.")
            return getUsedPlayerName(players)
        else:
            return None

def getValidUserString(prompt: str) -> str:
    '''Return user string without invalid characters.'''
    try: 
        name = input(prompt)
    except KeyboardInterrupt:
        clear()
        print("Menu cancelled!")
        return None
    if CSV_DELIM in name:
        print(f"Input cannot have \'{CSV_DELIM}\' in it.")
        return getValidUserString(prompt)
    return name

def getValidUserInt(prompt: str, lowerBound: int, upperBound: int) -> int:
    '''Return user int in [lowerBound, upperBound].'''
    try:
        out = input(prompt)
    except KeyboardInterrupt:
        clear()
        print("Menu cancelled!")
        return None
    try:
        out = int(out)
        return out
    except (ValueError, TypeError):
        print(f"Value must be an int in [{lowerBound}, {upperBound}]!")
        return getValidUserInt(prompt, lowerBound, upperBound)

def userYesNo(prompt: str) -> bool:
    inn = input(prompt)
    return inn.upper() == 'Y'

def plurify(string: str, num: int) -> str:
    if string[-1] == 's':
        string = string[0: len(string) - 1]
    if num > 1:
        return f"{string}s"
    return string

def rng(chance: int) -> bool:
    '''Has chance/100 chance of returning True'''
    if(chance >= 100):
        return True
    if(chance <= 0):
        return False
    return random.randint(0, 100) <= chance

class AdventureGame:
    def __init__(self) -> None:
        self.LOCATIONS = []
        self.ARMORS = []
        self.WEAPONS = []
        self.CREATURES = []
        self.PLAYERS = []
        self.player = None
        # Check files
        failed = False
        if(not exists(FILE_LOCATIONS)):
            print("ERROR loading Locations File!")
            failed = True
        if(not exists(FILE_ARMORS)):
            print("ERROR loading Armors File!")
            failed = True
        if(not exists(FILE_WEAPONS)):
            print("ERROR loading Weapons File!")
            failed = True
        if(not exists(FILE_CREATURES)):
            print("ERROR loading Creatures File!")
            failed = True
        if(failed):
            print("Aborting game...")
            return None

        # Start loading resources    
        with open(FILE_LOCATIONS, 'r') as f:
            aspects = f.readline().strip(",\n").split(CSV_DELIM)
            for line in f:
                newLocation = Location(line, aspects)
                self.LOCATIONS.append(newLocation)

        with open(FILE_ARMORS, 'r') as f:
            aspects = f.readline().strip(",\n").split(CSV_DELIM)
            for line in f:
                newArmor = Armor(line, aspects)
                self.ARMORS.append(newArmor)

        with open(FILE_WEAPONS, 'r') as f:
            aspects = f.readline().strip(",\n").split(CSV_DELIM)
            for line in f:
                newWeapon = Weapon(line, aspects)
                self.WEAPONS.append(newWeapon)

        with open(FILE_CREATURES, 'r') as f:
            aspects = f.readline().strip(",\n").split(CSV_DELIM)
            for line in f:
                newCreature = Creature(line, aspects)
                armor = newCreature.armor
                wep = newCreature.weapon
                newCreature.armor = self.ARMORS[[armor.name for armor in self.ARMORS].index(armor)]
                newCreature.weapon = self.WEAPONS[[weapon.name for weapon in self.WEAPONS].index(wep)]
                self.CREATURES.append(newCreature)

        self.loadPlayers()
    
    def loadPlayers(self):
        if not exists(FILE_PLAYERS):
            with open(FILE_DEFAULT_PLAYERS, 'r') as f:
                defaultPlayerLines = f.readlines()
            with open(FILE_PLAYERS, 'x') as f:
                f.writelines(defaultPlayerLines)
        with open(FILE_PLAYERS, 'r') as f:
            aspects = f.readline().strip(",\n").split(CSV_DELIM)
            for line in f:
                if line.strip(",\n").split(CSV_DELIM)[0][0] == '#': # Comments
                    continue
                if(len(line.strip(",\n").split(CSV_DELIM)) == len(aspects)):
                    newPlayer = Player()
                    newPlayer.loadFromLine(line, aspects)
                    loc = newPlayer.location
                    armor = newPlayer.armor
                    wep = newPlayer.weapon
                    newPlayer.location = self.LOCATIONS[[location.name for location in self.LOCATIONS].index(loc)]
                    newPlayer.armor = self.ARMORS[[armor.name for armor in self.ARMORS].index(armor)]
                    newPlayer.weapon = self.WEAPONS[[weapon.name for weapon in self.WEAPONS].index(wep)]
                    newPlayer.update()
                    self.PLAYERS.append(newPlayer)

    def getNewPlayer(self, ignorePlayerOverwrite: bool = False):
        clear()
        print("--- New Player Creation ---")
        newPlayer = Player()
        if(ignorePlayerOverwrite):
            newPlayer.name = getValidUserString("What is your name? : ").strip()
        else:
            newPlayer.name = getUnusedPlayerName(self.PLAYERS).strip()
        newPlayer.species = getValidUserString("What species are you? : ").strip()

        # Starter choice.
        print("Would you rather have... ")
        choice = getMenu("More starting health", "More starting speed", "More starting gold")
        if choice == 1:
            newPlayer.baseHealth = 15
            newPlayer.currentHealth = 15
        elif choice == 2:
            newPlayer.baseSpeed = 45
            newPlayer.currentSpeed = 45
        elif choice == 3:
            newPlayer.gold = 20
        else:
            clear()
            print("Creation cancelled!")
            return None
        print("An excellent choice.")

        # Location choice.     
        print("\nWhere would you like to start out?")
        starterLocs = [loc for loc in self.LOCATIONS if loc.starter]
        choice = getMenu(*[f"{loc.name} in the country of {loc.country}" for loc in starterLocs])
        if choice:
            newPlayer.location = starterLocs[choice-1]
        else:
            clear()
            print("Creation cancelled!")
            return None
        print(f"I knew someone from {newPlayer.location.name} once. What a {random.choice(ADJECTIVES_GOOD)} place!")

        # Weapon choice.
        print("\nNow, what weapon would you like to start with?")
        starterWeps = [wep for wep in self.WEAPONS if wep.starter]
        choice = getMenu(*[f"{wep.name}, a {wep.type} weapon dealing between {min(list(wep.damage))} and {max(list(wep.damage))} damage." for wep in starterWeps])
        if choice:
            newPlayer.weapon = starterWeps[choice-1]
        else:
            clear()
            print("Creation cancelled!")
            return None
        print(f"The {newPlayer.weapon.name} is a powerful tool in the hands of a competent warrior.")

        # Armor choice.
        print("\nFinally, you must choose your armor.")
        starterArmor = [armor for armor in self.ARMORS if armor.starter and armor.player]
        choice = getMenu(*[f"{armor.name} which slows you down by {armor.speedPenalty:.0%}, but negates {armor.protection:.0%} of incoming damage." for armor in starterArmor])
        if choice:
            newPlayer.armor = starterArmor[choice-1]
        else:
            clear()
            print("Creation cancelled!")
            return None
        print(f"Your new {newPlayer.armor.name} will serve you well, provided you don't overdo it.")
        newPlayer.generator = getDefaultGenerator()
        newPlayer.update()
        self.player = newPlayer

    def loadPlayer(self):
        clear()
        if(len(self.PLAYERS) == 0):
            print("No players to load.\n")
            return None
        try:
            playerName = getUsedPlayerName(self.PLAYERS)
            for player in self.PLAYERS:
                if playerName == player.name:
                    self.player = player
                    self.player.new = False
                    break
        except KeyboardInterrupt:
            self.player = None

    def savePlayer(self):
        player = self.player
        player.update()
        found = False
        with open(FILE_PLAYERS, 'r') as f:
            lines = f.readlines()
        for index, line in enumerate(lines):
            if player.name in line:
                found = True
                break
        if found:
            lines[index] = "".join(f"{value}," for value in self.player.generator.values()) + "\n"
        else:
            lines.append("".join(f"{value}," for value in self.player.generator.values()) + "\n") 
        with open(FILE_PLAYERS, 'w') as f:
            f.writelines(lines)
        player.new = False

    def viewStats(self):
        player = self.player
        print("--- Player Stats ---")
        if player.currentHealth <= 0:
            player.currentHealth = 0
            print(f"{player.name} the {player.species} is dead!")
        else:
            print(f"{player.name} the {player.species} is at {player.location.name}")
            print(f"They are level {player.level} and have {player.gold} gold pieces")
        print(f"Weapon: {player.weapon.name}, {min(player.weapon.damage)} to {max(player.weapon.damage)} damage")
        print(f"Armor: {player.armor.name}, slows {player.armor.speedPenalty:.0%} and negates {player.armor.protection:.0%} of {DAMAGE_TYPE_INV[player.armor.protectionType]} damage")  
        print(f"Health: {player.currentHealth}/{player.baseHealth} ({player.currentHealth/player.baseHealth:.0%})")
        print(f"Speed: {player.currentSpeed}/{player.baseSpeed} ({player.currentSpeed/player.baseSpeed:.0%})")

    def viewScoreboard(self):
        if len(self.PLAYERS) == 0:
            print("No players!")
            return None
        for player in self.PLAYERS:
            print(f"{player.name} the {player.species} is at {player.location.name}. They are level {player.level}.")

    def startGame(self):
        player = self.player
        round = 1
        if(round == 1 and not player.new):
            print(f"Welcome back to {player.location.name}, brave warrior.")
        elif(round == 1 and player.new):
            print(f"Welcome to {player.location.name}, brave warrior.")
        status = int(player.status)
        if(status == PLAYER_STATUS["sleeping"]):
            print(f"You were sleeping {random.choice(PLACES_SLEEPING)}, but you just woke up.")
            player.status = PLAYER_STATUS["idle"]
            round += 1
            self.idleMenu()
        elif(status == PLAYER_STATUS["fighting"]):
            print("You collapsed in the fight you were in!")
            print("You wake up near where you left off.")
            player.status = PLAYER_STATUS["idle"]
            round += 1
            self.idleMenu()
        elif(status == PLAYER_STATUS["resting"] or status == PLAYER_STATUS["idle"]):
            round += 1
            self.idleMenu()
        elif(status == PLAYER_STATUS["travelling"]):
            print(f"You are on your way to {player.location.name}.")
            round += 1
            self.travelMenu()
            self.startGame()

    def idleMenu(self):
        player = self.player
        alive = player.currentHealth > 0
        if not alive:
            print(f"{player.name} has passed away! Cannot play with this character.")
        else:
            print(f"You have a couple of options on how to proceed: ")
            fightPlace = random.choice(PLACES_FIGHT)
            choice = getMenu(f"Go to the {fightPlace} of {player.location.name} to fight", f"Go to the markets of {player.location.name} to shop", f"Return to {player.location.name} to sleep {random.choice(PLACES_SLEEPING)}", f"Travel to a distant city")
            if choice == 1:
                clear()
                player.status = PLAYER_STATUS["fighting"]
                self.fightMenu(fightPlace=fightPlace, round=1)
                self.idleMenu()
            elif choice == 2:
                clear()
                print(f"Welcome to the markets of {player.location.name}, {player.name}!")
                print(f"There are many treasures here; just don't waste all your gold!")
                self.marketMenu()
                player.update()
                self.idleMenu()
            elif choice == 3:
                clear()
                player.status = PLAYER_STATUS["sleeping"]
                print(f"You decide to return to {player.location.name} for the night.")
                if(userYesNo("Would you like to stop playing? (Y/N): ")):
                    pass
                else:
                    self.startGame()
            elif choice == 4:
                clear()
                self.travelMenu()
                self.idleMenu()
            else: #IE KeyboardInterrupt
                pass

    def marketMenu(self):
        player = self.player
        wepItems = []
        wepItemsPrompt = []
        armorItems = []
        armorItemsPrompt = []
        for wep in self.WEAPONS:
            if wep.player and wep.market and wep != player.weapon:
                wepItemsPrompt.append(f"{wep.cost} gold: {wep.name} ({wep.type}, {min(wep.damage)}-{max(wep.damage)} dmg)")
                wepItems.append(wep)
        for armor in self.ARMORS:
            if armor.player and armor.market and armor != player.armor:
                armorItemsPrompt.append(f"{armor.cost} gold: {armor.name} ({armor.protection:.0%} prot, -{armor.speedPenalty:.0%} speed)")
                armorItems.append(armor)
        print(f"Balance: {player.gold} gold")
        choice = getMenu("Buy a new weapon", "Buy a new armor", "Buy a healing potion", "Leave the market")
        if choice == 1:
            clear()
            print(f"Balance: {player.gold} gold")
            print(f"Current weapon: {player.weapon.name} ({min(player.weapon.damage)}-{max(player.weapon.damage)})")
            print(f"What weapon would you like to buy?")
            choiceWep = getMenu(*wepItemsPrompt)
            try:
                choiceWep -= 1
            except TypeError:
                choiceWep = None
            if choiceWep:
                if player.gold >= wepItems[choiceWep].cost:
                    player.weapon = wepItems[choiceWep]
                    player.gold -= wepItems[choiceWep].cost
                    print(f"Good luck with your new {player.weapon.name}, brave warrior!")
                elif choiceWep >= 0:
                    print(f"You don't have enough gold for a new {wepItems[choiceWep].name}!")
            self.marketMenu()
        elif choice == 2:
            clear()
            print(f"Balance: {player.gold} gold")
            print(f"Current armor: {player.armor.name} ({player.armor.protection:.0%} prot, -{player.armor.speedPenalty:.0%} speed)")
            print(f"What armor would you like to buy?")
            choiceArmor = getMenu(*armorItemsPrompt)
            try:
                choiceArmor -= 1
            except TypeError:
                choiceArmor = None
            if choiceArmor:
                if player.gold >= armorItems[choiceArmor].cost:
                    player.armor = armorItems[choiceArmor]
                    player.gold -= wepItems[choiceArmor].cost
                    print(f"Good luck with your new {player.armor.name}, brave warrior!")
                elif choiceArmor >= 0:
                    print(f"You don't have enough gold for a new {armorItems[choiceArmor].name}!")
                self.marketMenu()
        elif choice == 3:
            clear()
            if(player.currentHealth < player.baseHealth):
                print(f"Balance: {player.gold} gold")
                print(f"Health: {player.currentHealth}/{player.baseHealth} ({player.currentHealth/player.baseHealth:.0%})\n")
                print(f"We will heal 1 health per 1 gold!")
                healAmt = getValidUserInt(f"How much would you like to heal? (1-{player.baseHealth-player.currentHealth} HP): ", 1, player.baseHealth-player.currentHealth)
                if healAmt:
                    player.currentHealth += healAmt
                    player.gold -= healAmt
                    clear()
                    print(f"You healed for {healAmt} HP!")
                else:
                    clear()
                    print(f"Healing cancelled!")
            else:
                clear()
                print(f"You are already at full health! ({player.currentHealth}/{player.baseHealth})")
            self.marketMenu()
        else: #ie leaves / KeyboardInterrupt
            clear()
            print(f"You leave the markets of {player.location.name}.")

    def fightMenu(self, fightPlace: str, round: int = 1):
        player = self.player
        hostile = random.choice([creature for creature in self.CREATURES if not creature.friendly and creature.baseHealth <= player.baseHealth])
        hostileHP = hostile.baseHealth
        hostileArmor = hostile.armor
        hostileWep = hostile.weapon
        distance = random.randint(1, 60)
        clear()
        if(round == 1):
            print(f"You decide to go to the {fightPlace} to fight off the hordes that surely exist there.")
            print(f"In fact, before you could even get to the {fightPlace}, a crazy looking {hostile.species} appeared!")
            print(f"Stay away from its {random.choice(ADJECTIVES_BAD)} {hostileWep.name}!")
        else:
            print(f"Roaming the {fightPlace}, you come across a hostile {hostile.species}!")
            print(f"With its {random.choice(ADJECTIVES_BAD)} {hostileWep.name} ready, it approaches you!")
        alive = player.currentHealth > 0
        while(hostileHP > 0 and alive):
            distance = int(distance)
            player1Str = f"{player.name} the {player.species}"
            player2Str = f"HP: {player.currentHealth}/{player.baseHealth}"
            player3Str = f"WEP: {player.weapon.name} ({min(player.weapon.damage)}-{max(player.weapon.damage)})"
            hostile1Str = f"{hostile.name} the {hostile.species}"
            hostile2Str = f"HP: {hostileHP}/{hostile.baseHealth}"
            hostile3Str = f"WEP: {hostile.weapon.name} ({min(hostile.weapon.damage)}-{max(hostile.weapon.damage)})"
            sideWidth = max(len(player1Str), len(player2Str), len(player3Str))
            midWidth = 6
            midStr = '|'*midWidth
            print(f"{'~'*sideWidth} Fight! {'~'*sideWidth}")
            print(f"{player1Str:<{sideWidth}} {midStr:^{midWidth}} {hostile1Str:<{sideWidth}}")
            print(f"{player2Str:<{sideWidth}} {midStr:^{midWidth}} {hostile2Str:<{sideWidth}}")
            print(f"{player3Str:<{sideWidth}} {midStr:^{midWidth}} {hostile3Str:<{sideWidth}}")
            withinRange = player.weapon.range >= distance
            if withinRange:
                message = "within"
            else: 
                message = "not within"
            meters = plurify("meter", distance)
            print(f"It's {distance:d} {meters} away! You are {message} range!")
            retreated = False
            approached = False
            waited = False
            attacked = False
            healed = False
            escaped = False
            failedEscape = False
            # PLAYER TURN
            if withinRange:
                choice = getMenu(f"Attack the {hostile.species} with your {player.weapon.name}!", f"Retreat and consider your options")
                if choice == 1:
                    clear()
                    attacked = True
                    damageDealt = random.choice(player.weapon.damage)
                    if(player.weapon.damageType == hostile.armor.protectionType):
                        damageDealt = damageDealt - math.ceil(hostile.armor.protection * damageDealt)
                    hostileHP -= damageDealt
                    print(f"You use all your might and unleash your {player.weapon.name} against {hostile.name}!")
                    print(f"You dealt {damageDealt} damage!")
                    if hostileHP <= 0: ### WON FIGHT
                        hostileHP = 0
                        goldDrop = random.randint(int(hostile.baseHealth/4), hostile.baseHealth)
                        expDrop = random.randint(int(hostile.baseHealth/2), hostile.baseHealth)
                        player.gold += goldDrop
                        player.exp += expDrop
                        print(f"You killed {hostile.name} the {hostile.species}!")
                        goldPlusMsg = ""
                        if goldDrop > 0:
                            goldPlusMsg = f" ({player.gold})"
                        print(f"{goldDrop} gold flies out of their dead carcass!{goldPlusMsg}")
                        print(f"You won the fight!")
                        itemDrops = []
                        if(hostile.weapon.drop and hostile.weapon.player and hostile.weapon != player.weapon and rng(hostile.weapon.dropChance)):
                            itemDrops.append(hostile.weapon)
                        if(hostile.armor.drop and hostile.armor.player and hostile.armor != player.armor and rng(hostile.armor.dropChance)):
                            itemDrops.append(hostile.armor)
                        for item in itemDrops:
                            if type(item) is Weapon:
                                print(f"It dropped its {hostile.weapon.name} ({min(hostile.weapon.damage)}-{max(hostile.weapon.damage)})!")
                                if userYesNo(f"Would you like to replace your weapon with it? (Y/N): "):
                                    player.weapon = hostile.weapon
                            elif type(item) is Armor:
                                print(f"It dropped its {hostile.armor.name} ({hostile.armor.protection}% prot, {hostile.armor.speedPenalty}% speed penalty)!")
                                if userYesNo("Would you like to replace your armor with it? (Y/N): "):
                                    player.armor = hostile.armor
                        player.update()
                        break
                elif choice == 2:
                    clear()
                    retreated = True
                    oldDist = distance
                    hostileApproach = random.randint(int(hostile.baseSpeed/2), hostile.baseSpeed)
                    distance += player.currentSpeed - hostileApproach
                    if distance < 1:
                        distance = 1
                    if(distance > oldDist):
                        print(f"You retreat slightly!")
                    else:
                        print(f"You try to retreat, but the {hostile.species} is faster than you!")
                else:
                    hostileHP = -1
                    break
            else: # Not within range
                if(player.currentHealth < player.baseHealth):
                    choice = getMenu(f"Close the distance to try to attack the {hostile.species}", f"Wait for the {hostile.species} to approach", "Escape back to safety", f"Quickly patch your wounds (+{min(2, player.baseHealth-player.currentHealth)} HP)")
                else:
                    choice = getMenu(f"Close the distance to try to attack the {hostile.species}", f"Wait for the {hostile.species} to approach", "Escape back to safety")
                if choice == 1:
                    distance = distance - player.currentSpeed
                    if distance < 1:
                        distance = 1
                    approached = True
                    meters = plurify("meter", distance)
                    clear()
                    print(f"You closed the distance!")
                elif choice == 2:
                    waited = True
                    clear()
                    print(f"You waited for the {hostile.species} to close the distance!")
                elif choice == 3:
                    if(rng(60) or player.currentSpeed > (hostile.baseSpeed + 20) or distance > player.currentSpeed-(hostile.baseSpeed+20)):
                        escaped = True
                        clear()
                        print(f"You run away as fast as you can, escaping {hostile.name} the {hostile.species}!")
                        hostileHP = -1
                        break
                    else:
                        failedEscape = True
                        distance += random.randint(0-int(hostile.baseSpeed/2), hostile.baseSpeed)
                        clear()
                        print(f"You try to run away, but the {hostile.species} is too fast to escape that easily!")
                elif choice == 4:
                    clear()
                    healed = True
                    print(f"You chose to patch your wounds for {min(2, player.baseHealth-player.currentHealth)} HP!")
                    player.currentHealth += min(2, player.baseHealth-player.currentHealth)
                else:
                    hostileHP = -1
                    break
            # HOSTILE TURN
            withinRange = hostile.weapon.range >= distance
            if(not withinRange):
                if(attacked or approached):
                    distance -= random.randint(int(hostile.baseSpeed*0.75), hostile.baseSpeed)
                elif(failedEscape or retreated):
                    distance -= random.randint(int(hostile.baseSpeed*0.75), hostile.baseSpeed)
                elif(healed or waited):
                    distance -= random.randint(hostile.baseSpeed, hostile.baseSpeed*2)
                if(distance < 1):
                    distance = 1
                distance = int(distance)
                print(f"The {hostile.species} closes the distance to {distance} meters")
            withinRange = hostile.weapon.range >= distance
            if(withinRange and hostileHP > 0):
                if(attacked or failedEscape or healed or retreated):
                    damageDealt = player.doDamage(random.choice(hostile.weapon.damage), hostile.weapon.damageType)
                    print(f"The {hostile.species} angrily attacks you with their {hostile.weapon.name}!")
                    print(f"They dealt {damageDealt} damage!")
                elif(escaped):
                    print(f"The {hostile.species} tries to attack you once more with their {hostile.weapon.name}, but you're already gone!")
                    hostileHP = -1
                elif(approached):
                    print(f"The {hostile.species} approaches you as well!")
                    pass
            else:
                if(attacked or approached):
                    print(f"The {hostile.species} can't reach you with their {hostile.weapon.name}, but they are closing range rapidly!")
                elif(failedEscape or retreated):
                    print(f"Luckily, the {hostile.species} is still too far away to attack you! They are gaining still!")
                elif(healed or waited):
                    print(f"Fortunately, the {hostile.species} is still too far away to attack you! However, they are rapidly gaining!")
                elif(escaped):
                    print(f"You escape {hostile.name} easily!")
                    hostileHP = -1
            if player.currentHealth <= 0:
                alive = False
                print(f"You have died!")
                print(f"Game Over.")
        if(alive and userYesNo(f"Would you like to continue fighting at {fightPlace} of {player.location.name}? (Y/N): ") and alive):
            self.fightMenu(fightPlace=fightPlace, round=round+1)
        else:
            clear()
            print(f"You've returned to {player.location.name} after a long day of fighting.")
            pass

    def travelMenu(self):
        print(f"There are many cities available! Where would you like to go?")
        plpos = self.player.location.position
        locmenu = [f"{location.name} in {location.country}, {math.sqrt((plpos[0] - location.position[0])**2+(plpos[1] - location.position[1])**2):.1f} miles away" for location in self.LOCATIONS if location != self.player.location]
        choice = getMenu(*locmenu)
        if choice:
            chosen_loc = self.LOCATIONS[choice]
            clear()
            print(f"{chosen_loc.name} is a beautiful city! Good luck there, brave warrior!")
            self.player.location = chosen_loc
        else:
            print(f"Cancelled travelling!")

class Player:
    def __init__(self):
        self.new = True
        self.name = ""
        self.species = ""
        self.level = 1
        self.exp = 0
        self.gold = 5
        self.baseHealth = 10
        self.currentHealth = 10
        self.baseSpeed = 30
        self.currentSpeed = 30
        self.location = None
        self.armor = None
        self.weapon = None
        self.status = PLAYER_STATUS["sleeping"]

    def loadFromLine(self, line: str, aspects: str) -> None:
        '''Load player from a line in FILE_PLAYERS'''
        lline = line.strip(",\n").split(CSV_DELIM)
        genDict = {aspects[i]: lline[i] for i in range(len(aspects))}
        try:
            self.generator = genDict
            self.new = False
            self.name = genDict['name']
            self.species = genDict['species']
            self.level = int(genDict['level'])
            self.exp = int(genDict['exp'])
            self.gold = int(genDict['gold'])
            self.baseHealth = int(genDict['baseHealth'])
            self.currentHealth = int(genDict['currentHealth'])
            self.baseSpeed = int(genDict['baseSpeed'])
            self.currentSpeed = int(genDict['currentSpeed'])
            self.location = genDict['location']
            self.armor = genDict['armor']
            self.weapon = genDict['weapon']
            self.status = genDict['status']
        except KeyError:
            print("WARNING: Error loading players!")

    def doDamage(self, damage: int, damageType: int):
        if(damageType == self.armor.protectionType):
            damage = math.ceil(damage - (self.armor.protection * damage))
        self.currentHealth -= damage
        if(self.currentHealth < 0):
            self.currentHealth = 0
        return damage

    def update(self):
        self.updateSpeed()
        self.updateGenerator()
        self.updateLevel()

    def updateGenerator(self):
        genDict = self.generator
        genDict['name'] = str(self.name)
        genDict['species'] = str(self.species)
        genDict['level'] = int(self.level)
        genDict['exp'] = int(self.exp)
        genDict['gold'] = int(self.gold)
        genDict['baseHealth'] = int(self.baseHealth)
        genDict['currentHealth'] = int(self.currentHealth)
        genDict['baseSpeed'] = int(self.baseSpeed)
        genDict['currentSpeed'] = int(self.currentSpeed)
        genDict['location'] = self.location.name
        genDict['armor'] = self.armor.name
        genDict['weapon'] = self.weapon.name
        genDict['status'] = self.status

    def updateSpeed(self):
        '''Refresh speed'''
        speedPenalty = self.armor.speedPenalty
        self.currentSpeed = math.ceil(self.baseSpeed - (speedPenalty * self.baseSpeed))

    def updateLevel(self):
        oldLevel = self.level
        self.level = math.floor((self.exp+25) / 25)
        if(self.level > oldLevel):
            print(f"You levelled up to level {self.level} and gained +1 max HP!")
            self.baseHealth += 1
        else:
            self.level = oldLevel

class Creature:
    def __init__(self, line: str, aspects: str):
        lline = line.strip(",\n").split(CSV_DELIM)
        genDict = {aspects[i]: lline[i] for i in range(len(aspects))}
        try:
            self.generator = genDict
            self.name = genDict['name']
            self.species = genDict['species']
            self.baseHealth = int(genDict['baseHealth'])
            self.baseSpeed = int(genDict['baseSpeed'])
            self.armor = genDict['armor']
            self.weapon = genDict['weapon']
            self.friendly = INTERPRET_BOOL[genDict['friendly']]
        except KeyError:
            print("WARNING: Error loading creatures!")
            return None

class Location:
    def __init__(self, line: str, aspects: str):
        lline = line.strip(",\n").split(CSV_DELIM)
        genDict = {aspects[i]: lline[i] for i in range(len(aspects))}
        try:
            self.generator = genDict
            self.name = genDict['name']
            self.country = genDict['country']
            # Convert position into tuple of ints
            posList = genDict['position'].split(CSV_TUP_DELIM)
            self.position = tuple([int(x) for x in posList])
            self.starter = INTERPRET_BOOL[genDict['starter']]
        except KeyError:
            print("WARNING: Error loading locations!")
            return None

class Armor:
    def __init__(self, line: str, aspects: str):
        lline = line.strip(",\n").split(CSV_DELIM)
        genDict = {aspects[i]: lline[i] for i in range(len(aspects))}
        try:
            self.generator = genDict
            self.name = genDict['name']
            self.speedPenalty = float(genDict['speedPenalty'])
            self.protection = float(genDict['protection'])
            self.protectionType = DAMAGE_TYPE[genDict['protectionType']]
            self.starter = INTERPRET_BOOL[genDict['starter']]
            self.player = INTERPRET_BOOL[genDict['player']]
            self.market = INTERPRET_BOOL[genDict['market']]
            self.cost = int(genDict['cost'])
            self.drop = INTERPRET_BOOL[genDict['drop']]
            self.dropChance = int(genDict['dropChance'])
        except KeyError:
            print("WARNING: Error loading armors!")
            return None

class Weapon:
    def __init__(self, line: str, aspects: str):
        lline = line.strip("\n").split(CSV_DELIM)
        genDict = {aspects[i]: lline[i] for i in range(len(aspects))}
        try:
            self.generator = genDict
            self.name = genDict['name']
            self.type = genDict['type']
            self.range = int(genDict['range'])
            bounds = [int(x) for x in genDict['damageRange'].split(CSV_TUP_DELIM)]
            self.damage = range(bounds[0], bounds[1]+1)
            self.damageType = DAMAGE_TYPE[genDict['damageType']]
            self.starter = INTERPRET_BOOL[genDict['starter']]
            self.player = INTERPRET_BOOL[genDict['player']]
            self.market = INTERPRET_BOOL[genDict['market']]
            self.cost = int(genDict['cost'])
            self.drop = INTERPRET_BOOL[genDict['drop']]
            self.dropChance = int(genDict['dropChance'])
        except KeyError:
            print("WARNING: Error loading weapons!")
            return None