#!python

# Trio! state
# author: Robert Keller, Kim Merrill

from random import randrange
from alphabeta import alphaBeta, defaultFirstMove

# A state is a rows x rows board with attributes attributes.
# For now rows and attributes are as specified as constants
# Can be changed by changing constants, but search will slow

rows = 3
attributes = 3

empty = -1
interCellGap = " "

class State:
# state represents the board, next piece to be played, and other relevant info
    def __init__(self, verboseMode):
        """ Construct a new board. """
        self.rows = rows
        self.attributes = attributes
        self.pieces = pow(2, attributes)
        self.cells = self.rows * self.rows
        self.emptyRow = tuple([empty for col in range(rows)])
        self.board = tuple([self.emptyRow for row in range(rows)])
        
        # Initialize list of pieces and cells
        self.firstPiece = 0
        self.unplayedPieces = range(self.pieces)
        self.unoccupiedCells = range(self.cells)
        self.pieceToPlay = self.firstPiece
        self.verboseMode = verboseMode

    def copy(self):
        """ Make a copy of this State. """
        newState = State(self.verboseMode)
        newState.unplayedPieces = list(self.unplayedPieces)
        newState.unoccupiedCells = list(self.unoccupiedCells)
        newState.pieceToPlay = self.pieceToPlay
        boardAsList = list(map(list, self.board))
        newState.board = tuple(map(tuple, boardAsList))
        return newState

    def setPieceToPlay(self, piece):
        """ Set the next piece to be played. """
        self.pieceToPlay = piece

    def getPieceToPlay(self):
        """ Get the next piece to be played. """
        return self.pieceToPlay

    def placePieceInSearch(self, cell):
        """ Place piece to play in indexed cell while searching. """
        if self.verboseMode:
            # Prints all states searched if command line option toggled.
            print "Searched state: placing " + str(self.pieceToPlay) + " in cell " + str(cell)
        self.place(cell)

    def placePieceInGame(self, cell):
        """ Place piece to play in indexed cell during gameplay. """
        print "Placing " + str(self.pieceToPlay) + " in cell " + str(cell)
        self.place(cell)

    def place(self, cell):
        """ Place piece to play in indexed cell. """
        row = cell // rows
        col = cell % rows
        boardAsList = list(map(list, self.board))
        boardAsList[row][col] = self.pieceToPlay
        self.board = tuple(map(tuple, boardAsList))
        self.unplayedPieces.remove(self.pieceToPlay)
        self.unoccupiedCells.remove(cell)

    def getUnplacedPieces(self):
        """ Return the list of pieces remaining to be placed. """
        return self.unplayedPieces

    def formatPieces(self, pieces):
        """ Displays piece with bit representation. """
        formattedPieces = []
        for piece in pieces:
            formattedPieces.append(str(piece) + " (" + self.renderAsBits(piece) + ")")
        return formattedPieces

    def getUnoccupiedCells(self):
        """ Return the list of unoccupied cells. """
        return self.unoccupiedCells

    def calculateNextMove(self):
        """ Determines best move. """
        if self.getPieceToPlay() == 0 and self.rows == 3 and self.attributes == 3:
            # Return default best start move instead of searching to improve runtime.
            return defaultFirstMove(self)
        else:
            return alphaBeta(self)

    def isUnoccupied(self, cell):
        """ Return whether given cell is occupied. """
        return cell in self.unoccupiedCells

    def isUnplaced(self, piece):
        """ Return whether given piece is unplayed. """
        return piece in self.unplayedPieces

    def isVerboseMode(self):
        """ Return whether command line option has been toggled. """
        return self.verboseMode

    def render(self):
        """ Render this state as a string. """
        rendering = "Piece to play: " + str(self.pieceToPlay) \
            + " (" + self.renderAsBits(self.pieceToPlay) + ")\n"

        for row in range(0, rows):
            rowRendering = ""
            for col in range(0, rows):
                rowRendering += self.renderAsBits(self.board[row][col])
                rowRendering += interCellGap
            rendering += rowRendering + "\n"
        return rendering

    def renderAsBits(self, cell):
        """ Render cell contents as a bit vector """
        if cell == None:
            return "none"
        cellRendering = ""
        if cell == empty:
            for attribute in range(0, self.attributes):
                cellRendering = cellRendering + "_"
        else:
            for attribute in range(0, self.attributes):
                cellRendering = ("0" if cell % 2 == 0 else "1") + cellRendering
                cell /= 2
        return cellRendering

    def checkRows(self, board):
        """ Check rows of board for win. """
        for row in board:
            emptyCell = False
            commonOnes = empty
            commonZeroes = 0
            for cell in row:
                if cell == empty:
                    # If any cells are empty, the row can't be a win.
                    emptyCell = True
                    break
                else:
                    # If win, either commonOnes != 000 or commonZeros = bit string of all 1s
                    commonOnes = commonOnes & cell
                    commonZeroes = commonZeroes | cell
            if not emptyCell:
                if commonOnes > 0 or commonZeroes != ((1<<len(board))-1):
                    return True
        return False

    def checkColumns(self, board):
        """ Check columns of board for win. """
        transposed = zip(*board)
        return self.checkRows(transposed)

    def checkLeftDiagonal(self, board):
        """ Check left diagonal of board for win. """
        emptyCell = False
        commonOnes = empty
        commonZeroes = 0
        for i in range(len(board)):
            cell = board[i][i]
            if cell == empty:
                # If any cells are empty, the diagonal can't be a win.
                emptyCell = True
                break
            # If win, either commonOnes != 0 or commonZeroes = bit string of all 1s
            commonOnes = commonOnes & cell
            commonZeroes = commonZeroes | cell
        if not emptyCell:
            return commonOnes > 0 or commonZeroes != ((1<<len(board))-1)

    def checkRightDiagonal(self, board):
        """ Check right diagonal of board for win. """
        rev = list(board)
        rev.reverse()
        return self.checkLeftDiagonal(rev)

    def tieGame(self):
        """" Check if the game has ended in a draw. """
        return len(self.unplayedPieces) == 0

    def gameOver(self):
        """ Check if the game has been won. """
        boardAsList = list(map(list, self.board))
        return self.checkRows(boardAsList) or self.checkColumns(boardAsList) or self.checkLeftDiagonal(boardAsList) or self.checkRightDiagonal(boardAsList)

