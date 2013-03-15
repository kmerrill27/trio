# Trio! CLI
# author: Robert Keller, Kim Merrill
# purpose: Presents a simple interface the Trio! game, as explained in assignment 3

import sys
from state import State

# To toggle verbose mode (print out all explored states and alpha/beta values), use command line option "v".
# To play QUARTO, use "quarto" command line option. For verbose quarto mode, use "quarto v."
# Quarto relies heavily on utility function, only searching to depth of 3.

messageComputersTurn     = "Computer's turn."
messageComputerWins      = "Computer wins."
messageChoosePlayer      = "Which player goes first? (1 = you, 2 = computer, 0 = stop) "
messageGoodbye           = "Goodbye. Thanks for playing Trio!."
messageTryAgain          = "That is invalid. Please try again."
messageUsersTurn         = "User's turn."
messageWelcome           = "Welcome to Trio!"
messageYouWin            = "User wins."
messageTie               = "Tie game."

userFirst = 1
computerFirst = 2

def main():
    """ Run the Trio! playing program. """
    print messageWelcome
    verboseMode = False
    quartoMode = False
    args = sys.argv
    # If command line option "v," enter verbose mode.
    if len(args) == 2:
        if args[1] == "v":
            print "Playing in verbose mode."
            verboseMode = True
        elif args[1] == "quarto":
            quartoMode = True
            print "Playing in quarto mode."
    elif len(args) == 3:
        if args[1] == "quarto" and args[2] == "v":
            verboseMode = True
            quartoMode = True
            print "Playing in verbose quarto mode."
    playUntilExit(verboseMode, quartoMode)

def playUntilExit(verboseMode, quartoMode):
    """ Play successive games until the user decides to stop. """
    while True:
        firstPlayer = getFirstPlayer()
        if firstPlayer == 0:
            print messageGoodbye    
            return
        playTrio(firstPlayer, verboseMode, quartoMode)

def getFirstPlayer():
    """ Get the first player, or an indication to stop. """
    while True:
	response = raw_input(messageChoosePlayer)
        if response == "1":
            return 1
        elif response == "2":
            return 2
        elif response == "0":
            return 0
        else:
            print messageTryAgain

def playTrio(firstPlayer, verboseMode, quartoMode):
    """ Play the game, given first player, or stop. """
    state = State(verboseMode, quartoMode)
    if firstPlayer == userFirst:
        userTurn(state)
    elif firstPlayer == computerFirst:
        computerTurn(state)
    else:
        assert "Should never happen"

def userTurn(state):
    """ Simulate one round of play with the user starting. """
    print messageUsersTurn
    print state.render()

    while True:
        cell = raw_input("Place piece " + str(state.getPieceToPlay()) + " at cell number: ")
        # Validate that input is an integer and corresponds to an unoccupied cell.
        # If not, prompt the user to enter another value.
        try:
            cell = int(cell)
            if state.isUnoccupied(cell):
                break
            else:
                print messageTryAgain
        except ValueError:
            print messageTryAgain

    state.placePieceInGame(cell)
    print state.render()

    # If game has been won, end game.
    if state.gameOver():
        print messageYouWin
        return
    elif state.tieGame():
        print messageTie
        return

    # If no pieces are left to play, return None.
    while True:
        nextPiece = raw_input("Designate next piece to play " + str(state.formatPieces(state.getUnplacedPieces())) + ": ")
        # Validate that input is an integer and corresponds to an unplaced piece.
        # If not, prompt the user to enter another value.
        try:
            nextPiece = int(nextPiece)
            if state.isUnplaced(nextPiece):
                break
            else:
                print messageTryAgain
        except ValueError: 
            print messageTryAgain

    state.setPieceToPlay(nextPiece)
    computerTurn(state)

def computerTurn(state):
    """ Simulate the computer's turn. """
    print messageComputersTurn
    print state.render()

    # Use alpha-beta search to find best move.
    nextState = state.calculateNextMove()
    print nextState.render()

    # If game has not ended, continue gameplay.
    if nextState.gameOver():
        print messageComputerWins
        return
    elif nextState.tieGame():
        print messageTie
        return
    else:
        userTurn(nextState)

# Run game
main()