#!python

# Trio! alpha-beta search
# author: Kim Merrill

minPlayer = 0
maxPlayer = 1
empty = -1

def defaultFirstMove(state):
	""" Return best possible first move for 3-row/3-attribute Trio game."""
	# Note: alphaBeta will return this same first move, but requires several seconds of search time.
	print "Using default first move."
	return makeMove([4,7], state)

def alphaBeta(state):
	""" Run alpha-beta search on Trio state with cuttof depth of 5, alpha = -inf, and beta = inf. """
	return alphaBetaSearch(state, 5, -float("inf"), float("inf"), 1)[1]

def alphaBetaSearch(state, depth, alpha, beta, player):
	""" Return best found move and corresponding alpha/beta value. """
	# Save best state found among children
	bestState = state
	# If depth cutoff reached or is a ending state, return heuristic cost estimate.
	if depth == 0 or isTerminal(state):
		return [costEstimate(state, depth), state]
	if player == maxPlayer:
		moves = expand(state)
		nextMove = moves.next()
		while nextMove != None:
			nextState = makeMove(nextMove, state)
			result = alphaBetaSearch(nextState, depth-1, alpha, beta, not player)
			# If command line option toggled, print alpha and beta values.
			if state.isVerboseMode():
				print "Alpha (MAX): old=" + str(alpha) + ", found=" + str(result[0]) +", new=" + str(max(alpha, result[0]))
				print "Beta (MAX): old=" + str(beta)
 			if alpha < result[0]:
 				# If current move is better than last best move, remember it.
				alpha = result[0]
				bestState = nextState
			if beta <= alpha:
				# Prune search tree.
				if state.isVerboseMode():
					print "Pruning (MAX)"
				break
			# Evaluate next move.
			nextMove = moves.next()
		return [alpha, bestState]
	else:
		moves = expand(state)
		nextMove = moves.next()
		while nextMove != None:
			nextState = makeMove(nextMove, state)
			result = alphaBetaSearch(nextState, depth-1, alpha, beta, not player)
			# If command line option toggled, print alpha and beta values.
			if state.isVerboseMode():
				print "Alpha (MIN): " + str(alpha)
				print "Beta (MIN): old=" + str(beta) +", found=" + str(result[0]) + " new=" + str(min(beta, result[0]))
			if beta > result[0]:
				# If current move is better than last best move, remember it.
				beta = result[0]
				bestState = nextState
			if beta <= alpha:
				# Prune search tree.
				if state.isVerboseMode():
					print "Pruning (MIN)"
				break
			# Evaluate next move.
			nextMove = moves.next()
		return [beta, bestState]

def makeMove(move, state):
	""" Apply move to state and return resulting game state. """
	cell = move[0]
	piece = move[1]
	newState = state.copy()
	newState.placePieceInSearch(cell)
	newState.setPieceToPlay(piece)
	return newState

def expand(state):
	""" Return generator of all possible moves, which are [cell, piece] pairs. """
	for cell in state.getUnoccupiedCells():
		for piece in state.getUnplacedPieces():
			if piece != state.getPieceToPlay():
				yield [cell, piece]
	yield None

def isTerminal(state):
	""" Return whether state is a game-ending state. """
	return state.gameOver() or state.tieGame()

def countRows(board, opponentPiece):
	""" Return heuristic cost for rows of given board. """
	emptyCells = 0
	commonOnes = empty
	commonZeroes = 0
	cost = 0
	for row in board:
		for cell in row:
			if cell == empty:
				# Count number of empty cells in row.
				emptyCells += 1
			else:
				commonOnes = commonOnes & cell
				commonZeroes = commonZeroes | cell
		if opponentPiece != None:
			commonOnes = commonOnes & opponentPiece
			commonZeroes = commonZeroes | opponentPiece
		if commonOnes > 0 or commonZeroes != ((1<<len(board))-1):
			if emptyCells == 1:
				# Two pieces in row and attribute(s) in common with piece to be played.
				cost += 300
        	elif emptyCells == 2:
        		# One piece in row and attribute(s) in common with piece to be played.
        		cost -= 100
        emptyCells = 0
   	return cost

def countDiagonal(board, opponentPiece):
	""" Return heuristic cost for diagonal of given board. """
	emptyCells = 0
	commonOnes = empty
	commonZeroes = 0
	cost = 0
	for i in range(len(board)):
		cell = board[i][i]
		if cell == empty:
			# Count number of empty cells in diagonal.
			emptyCells += 1
        else:
        	commonOnes = commonOnes & cell
        	commonZeroes = commonZeroes | cell
	if opponentPiece != None:
		commonOnes = commonOnes & opponentPiece
		commonZeroes = commonZeroes | opponentPiece
	if commonOnes > 0 or commonZeroes != ((1<<len(board))-1):
		if emptyCells == 1:
			# Two pieces in diagonal and attribute(s) in common with piece to be played.
			cost += 300
		elif emptyCells == 2:
			# One piece in diagonal and attribute(s) in common with piece to be played.
			cost -= 100
	return cost

def costEstimate(state, depth):
	""" Return heuristic cost for current state. """
	cost = 0
	if state.tieGame():
		cost -= 5000
	elif state.gameOver():
		cost += 5000000
	else:
		board = state.board
		transposed = zip(*board)
		rev = list(board)
		rev.reverse()
		opponentPiece = state.getPieceToPlay()
		# Evaluate board based on the current placed pieces and piece to be given to the opponent to play.
		cost = countRows(board, opponentPiece) + countRows(transposed, opponentPiece) + countDiagonal(board, opponentPiece) + countDiagonal(rev, opponentPiece)
	# Weight by depth. A winning state that happens in the fewest moves is preferred.
	return cost*(depth+1)