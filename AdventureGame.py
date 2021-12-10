from os import system
from os.path import exists
import fileinput
import random
import math

clear = lambda: system('cls')

ADJECTIVES_BAD = ("evil", "disgusting", "dirty", "horrible", "awful", "terrible")
ADJECTIVES_GOOD = ("wonderful", "wondrous", "amazing", "awesome", "great", "fantastic")

PLACES_SLEEPING = ("in a tavern", "in a hostel", "on the street", "in an alleyway", "in a ditch", "in a garbage bin", "on a nice bed", "on a rooftop overlooking the town", "in a cozy place", "in an awfully smelly corner")
PLACES_FIGHT = ("forests", "outlying trade routes", "caves", "labyrinth", "abandoned mineshafts", "woodlands", "rolling hills", "mountains", "firey caves")

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
        aspects = f.readline().strip("\n").split(CSV_DELIM)
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
        try:
            name = input("What is your name? : ")
        except KeyboardInterrupt:
            clear()
            print("Menu cancelled!")
            return None
        for player in players:
            if name == player.name:
                print(f"{name} is already in use! Specify a unique name.")
                return getUnusedPlayerName(players)
        return name

def getUsedPlayerName(players: list):
        '''Check name and return if valid.'''
        try:
            name = input("What is your name? : ")
        except KeyboardInterrupt:
            clear()
            print("Menu cancelled!")
            return None
        for player in players:
            if name == player.name:
                print(f"{name} found!")
                return name
        print("Name not found. Specify a name that has been used.")
        return getUsedPlayerName(players)

def randomChoice(llist: list):
    '''Given a list, return a random element'''
    return llist[random.randint(0, len(llist)-1)]

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
                    newPlayer.updateSpeed()
                    newPlayer.updateLevel()
                    self.PLAYERS.append(newPlayer)

    def getNewPlayer(self, ignorePlayerOverwrite: bool = False):
        clear()
        print("--- New Player Creation ---")
        self.player = Player()
        try:
            if(ignorePlayerOverwrite):
                self.player.name = input("What is your name? : ").strip()
            else:
                self.player.name = getUnusedPlayerName(self.PLAYERS).strip()
            self.player.species = input("What species are you? : ").strip()
        except KeyboardInterrupt:
            clear()
            print("Creation cancelled!")
            return None

        # Starter choice.
        print("Would you rather have... ")
        choice = getMenu("More starting health", "More starting speed", "More starting gold")
        if(choice == 1):
            self.player.baseHealth = 15
            self.player.currentHealth = 15
        elif(choice == 2):
            self.player.baseSpeed = 45
            self.player.currentSpeed = 45
        elif(choice == 3):
            self.player.gold = 20
        else:
            clear()
            print("Creation cancelled!")
            return None
        print("An excellent choice.")

        # Location choice.       
        print("\nWhere would you like to start out?")
        starterLocs = [loc for loc in self.LOCATIONS if loc.starter]
        choice = getMenu(*[f"{loc.name} in the country of {loc.country}" for loc in starterLocs])
        if(choice):
            self.player.location = starterLocs[choice-1]
        else:
            clear()
            print("Creation cancelled!")
            return None
        print(f"I knew someone from {self.player.location.name} once.")

        # Weapon choice.
        print("\nNow, what weapon would you like to start with?")
        starterWeps = [wep for wep in self.WEAPONS if wep.starter]
        choice = getMenu(*[f"{wep.name}, a {wep.type} weapon dealing between {min(list(wep.damage))} and {max(list(wep.damage))} damage." for wep in starterWeps])
        if(choice):
            self.player.weapon = starterWeps[choice-1]
        else:
            clear()
            print("Creation cancelled!")
            return None
        print(f"The {self.player.weapon.name} is a powerful tool in the hands of a competent warrior.")

        # Armor choice
        print("\nFinally, you must choose your armor.")
        starterArmor = [armor for armor in self.ARMORS if armor.starter and armor.player]
        choice = getMenu(*[f"{armor.name} which slows you down by {armor.speedPenalty*100:.0f}%, but negates {armor.protection*100:.0f}% of incoming damage." for armor in starterArmor])
        if(choice):
            self.player.armor = starterArmor[choice-1]
        else:
            clear()
            print("Creation cancelled!")
            return None
        print(f"Your new {self.player.armor.name} will serve you well, provided you don't overdo it.")
        self.player.generator = getDefaultGenerator()
        self.player.updateLevel()
        self.player.updateSpeed()

    def loadPlayer(self):
        clear()
        if(len(self.PLAYERS) == 0):
            print("No players to load.\n")
            return None
        playerName = getUsedPlayerName(self.PLAYERS)
        for player in self.PLAYERS:
            if playerName == player.name:
                self.player = player
                self.player.new = False
                break

    def savePlayer(self):
        player = self.player
        player.updateGenerator()
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
        print(f"Armor: {player.armor.name}, slows {player.armor.speedPenalty*100:.0f}% and negates {player.armor.protection*100}% of {DAMAGE_TYPE_INV[player.armor.protectionType]} damage")  
        print(f"Health: {player.currentHealth}/{player.baseHealth} ({(player.currentHealth/player.baseHealth)*100:.0f}%)")
        print(f"Speed: {player.currentSpeed}/{player.baseSpeed} ({(player.currentSpeed/player.baseSpeed)*100:.0f}%)")

    def viewScoreboard(self):
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
            print(f"You were sleeping {randomChoice(PLACES_SLEEPING)}, but you just woke up.")
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
            fightPlace = randomChoice(PLACES_FIGHT)
            choice = getMenu(f"Go to the {fightPlace} of {player.location.name} to fight", f"Return to {player.location.name} to sleep {randomChoice(PLACES_SLEEPING)}", f"Travel to a distant city")
            if(choice == 1):
                clear()
                player.status = PLAYER_STATUS["fighting"]
                self.fightMenu(fightPlace=fightPlace, round=1)
                self.idleMenu()
            elif(choice == 2):
                clear()
                player.status = PLAYER_STATUS["sleeping"]
                print(f"You decide to return to {player.location.name} for the night.")
                if(userYesNo("Would you like to continue playing? (Y/N): ")):
                    self.startGame()
                else:
                    pass
            elif(choice == 3):
                clear()
                #TODO self.travelMenu()
                self.idleMenu()        

    def fightMenu(self, fightPlace: str, round: int = 1):
        player = self.player
        hostile = randomChoice([creature for creature in self.CREATURES if not creature.friendly])
        hostileHP = hostile.baseHealth
        hostileArmor = hostile.armor
        hostileWep = hostile.weapon
        distance = random.randint(1, 60)
        if(round == 1):
            print(f"You decide to go to the {fightPlace} to fight off the hordes that surely exist there.")
            print(f"In fact, before you could even get to the {fightPlace}, a crazy looking {hostile.name} appeared!")
            print(f"Stay away from its {randomChoice(ADJECTIVES_BAD)} {hostileWep.name}!")
        else:
            print(f"Roaming the {fightPlace}, you come across a hostile {hostile.name}!")
            print(f"With its {randomChoice(ADJECTIVES_BAD)} {hostileWep.name} ready, it approaches you!")
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
                if(choice == 1):
                    clear()
                    attacked = True
                    damageDealt = random.choice(player.weapon.damage)
                    if(player.weapon.damageType == hostile.armor.protectionType):
                        damageDealt = damageDealt - math.ceil(hostile.armor.protection * damageDealt)
                    hostileHP -= damageDealt
                    print(f"You use all your might and unleash your {player.weapon.name} against the {hostile.name}!")
                    print(f"You dealt {damageDealt} damage!")
                    if(hostileHP <= 0):
                        hostileHP = 0
                        goldDrop = random.randint(int(hostile.baseHealth/4), hostile.baseHealth)
                        expDrop = random.randint(int(hostile.baseHealth/2), hostile.baseHealth)
                        player.gold += goldDrop
                        player.exp += expDrop
                        print(f"You killed {hostile.name} the {hostile.species}!")
                        print(f"{goldDrop} gold flies out of their dead carcass!")
                        print(f"You won the fight!")
                        player.updateLevel()
                        break
                elif(choice == 2):
                    clear()
                    retreated = True
                    hostileApproach = random.randint(int(hostile.baseSpeed/2), hostile.baseSpeed)
                    distance += player.currentSpeed - hostileApproach
                    if(distance < 1):
                        distance = 1
                    if(player.currentSpeed > hostileApproach):
                        print(f"You retreat slightly!")
                    else:
                        print(f"You try to retreat, but the {hostile.species} is faster than you!")
            else: # Not within range
                if(player.currentHealth < player.baseHealth):
                    choice = getMenu(f"Close the distance to try to attack the {hostile.species}", f"Wait for the {hostile.species} to approach", "Escape back to safety", f"Quickly patch your wounds (+{min(2, player.baseHealth-player.currentHealth)} HP)")
                    if(choice == 4):
                        clear()
                        healed = True
                        print("You chose to patch your wounds for 2 HP!")
                        player.currentHealth += 2
                else:
                    choice = getMenu(f"Close the distance to try to attack the {hostile.species}", f"Wait for the {hostile.species} to approach", "Escape back to safety")
                if(choice == 1):
                    distance = distance - player.currentSpeed
                    if distance < 1:
                        distance = 1
                    approached = True
                    meters = plurify("meter", distance)
                    clear()
                    print(f"You closed the distance!")
                elif(choice == 2):
                    waited = True
                    clear()
                    print(f"You waited for the {hostile.species} to close the distance!")
                elif(choice == 3):
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
            # HOSTILE TURN
            withinRange = hostile.weapon.range >= distance
            if(withinRange and hostileHP > 0):
                if(attacked or failedEscape or healed or retreated):
                    damageDealt = player.updateHealth(random.choice(hostile.weapon.damage), hostile.weapon.damageType)
                    print(f"The {hostile.species} angrily attacks you with their {hostile.weapon.name}!")
                    print(f"They dealt {damageDealt} damage!")
                elif(escaped):
                    print(f"The {hostile.species} tries to attack you once more with their {hostile.weapon.name}, but you're already gone!")
                    hostileHP = -1
                elif(approached):
                    pass
            else:
                if(attacked or approached):
                    print(f"The {hostile.species} can't reach you with their {hostile.weapon.name}, but they are closing range rapidly!")
                    distance -= random.randint(int(hostile.baseSpeed*0.75), hostile.baseSpeed)
                elif(failedEscape or retreated):
                    print(f"Luckily, the {hostile.species} is still too far away to attack you! They are gaining still!")
                    distance -= random.randint(int(hostile.baseSpeed*0.5), hostile.baseSpeed)
                elif(healed or waited):
                    print(f"Fortunately, the {hostile.species} is still too far away to attack you! However, they are rapidly gaining!")
                    distance -= random.randint(hostile.baseSpeed, hostile.baseSpeed*2)
                if(distance < 1):
                    distance = 1
            if player.currentHealth <= 0:
                alive = False
                print(f"You have died!")
                print(f"Game Over.")
        if(alive and userYesNo(f"Would you like to continue towards the {fightPlace} of {player.location.name}? (Y/N): ") and alive):
            self.fightMenu(fightPlace=fightPlace, round=round+1)
        else:
            clear()
            print(f"You've returned to {player.location.name} after a long day of fighting.")
            pass

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
        self.currentSpeed = self.baseSpeed - (speedPenalty * self.baseSpeed)

    def updateHealth(self, damage: int, damageType: int):
        if(damageType == self.armor.protectionType):
            damage = math.ceil(damage - (self.armor.protection * damage))
        self.currentHealth -= damage
        if(self.currentHealth < 0):
            self.currentHealth = 0
        return damage

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
        except KeyError:
            print("WARNING: Error loading weapons!")
            return None