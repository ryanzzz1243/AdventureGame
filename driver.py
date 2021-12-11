import AdventureGame
import time
from os import system

# Clear console to get ready for input.
clear = lambda: system('cls')
game = AdventureGame.AdventureGame()

maxCancelTries = 2

def userYesNo(prompt: str) -> bool:
    inn = input(prompt)
    return inn.upper() == 'Y'

def mainMenu():
    print("--- Main Menu ---")
    choice = AdventureGame.getMenu("Start New Game", "Load Game", "Scoreboard", "Quit")
    if(choice == 1):
        try:
            game.getNewPlayer(ignorePlayerOverwrite=True)
        except AttributeError:
            game.player = None
        if(game.player):
            print("Game created successfully!")
            time.sleep(2)
            clear()
            print("Game created successfully!\n")
            loadedMenu()
        else:
            print("Error creating game! Going back to main menu...")
            game.player = None
            mainMenu()
    elif(choice == 2):
        game.loadPlayer()
        if(game.player):
            loadedMenu()
        else:
            mainMenu()
    elif(choice == 3):
        clear()
        game.viewScoreboard()
        print()
        mainMenu()
    elif(choice == 4):
        print("Goodbye.")
    else:
        print("Goodbye.")

def loadedMenu():
    choice = AdventureGame.getMenu("Play Game", "View Stats", "Save", "Save & Quit to Main Menu")
    if(choice == 1):
        clear()
        game.startGame()
        loadedMenu()
    elif(choice == 2):
        clear()
        game.viewStats()
        print()
        loadedMenu()
    elif(choice == 3):
        game.savePlayer()
        clear()
        print("Game saved!")
        loadedMenu()
    elif(choice == 4):
        game.savePlayer()
        clear()
        print("Game saved!")
        mainMenu()
    else:
        loadedMenu()

def main():
    clear()
    print("Welcome to your own Epic Super Adventure!")
    print("All code by Ryan Edwards rje7hp for IT4401 taught by Dale Musser")
    print("10 December 2021")
    print()
    mainMenu()

if __name__ == "__main__":
    main()