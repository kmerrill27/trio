#!python

# Trio! alpha-beta search
# author: Kim Merrill

minPlayer = -1
maxPlayer = 1
empty = -1
maxDepth = 5

def alphaBeta(state):
	""" Run alpha-beta search on Trio state with cuttof depth of 5, alpha = -inf, and beta = inf. """
	return alphaBetaSearch(state, maxDepth, -float("inf"), float("inf"), 1)[1]

def alphaBetaSearch(state, depth, alpha, beta, player):
	""" Return best found move and corresponding alpha/beta value. """
	bestMove = state
	# If depth cutoff reached or is a ending state, return heuristic cost estimate.
	if state.gameOver():
		# If command line option toggled, print states as found.
		if state.isVerboseMode():
			if player == maxPlayer:
				winFor = "MIN"
			else:
				winFor = "MAX"
			print "Winning state for " + winFor + " found in " + str(maxDepth-depth) + " move(s): " + state.render()
		return [(depth+1)*100000*-player, state]
	elif state.tieGame():
		# If command line option toggled, print states as found.
		if state.isVerboseMode():
			print "Tie state found in " + str(maxDepth-depth) + " move(s): " + state.render()
		return [(depth+1)*1000*-player, state]
	elif depth == 0:
		# Use static utility function to improve search time.
		return [costEstimate(state, player), state]
	if player == maxPlayer:
		moves = expand(state)
		nextMove = moves.next()
		while nextMove != None:
			nextState = makeMove(nextMove, state)
			result = alphaBetaSearch(nextState, depth-1, alpha, beta, not player)
			if result[0] > alpha:
				# If command line option toggled, print new alpha value.
				if state.isVerboseMode():
					print "MAX: old alpha=" + str(alpha) + ", new alpha=" + str(result[0])
				alpha = result[0]
				# Save current best move.
				bestMove = nextState
			# Prune if searching farther down branch is nonproductive.
			if beta <= alpha:
				if state.isVerboseMode():
					print "Pruning max."
				break
				# Check next move.
			nextMove = moves.next()
		return [alpha, bestMove]
	else:
		moves = expand(state)
		nextMove = moves.next()
		while nextMove != None:
			nextState = makeMove(nextMove, state)
			result = alphaBetaSearch(nextState, depth-1, alpha, beta, not player)
			if result[0] < beta:
				# If command line option toggled, print new beta value.
				if state.isVerboseMode():
					print "MIN: old beta=" + str(beta) + ", new beta=" + str(result[0])
				beta = result[0]
				# Save current best move.
				bestMove = nextState
			# Prune if searching farther down branch is nonproductive.
			if beta <= alpha:
				if state.isVerboseMode():
					print "Pruning min."
				break
			# Check next move.
			nextMove = moves.next()
		return [beta, bestMove]

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
	# Reverse list of unplaced pieces first to improve search time.
	# Best moves are more likely to select pieces that are opposite current piece.
	unplacedPieces = state.getUnplacedPieces()
	unplacedPieces.reverse()
	for cell in state.getUnoccupiedCells():
		if len(state.getUnplacedPieces()) == 1:
			yield [cell, None]
		else:
			for piece in unplacedPieces:
				if piece != state.getPieceToPlay():
					yield [cell, piece]
	yield None

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
				cost += 200
        	elif emptyCells == 2:
        		# One piece in row and attribute(s) in common with piece to be played.
        		cost -= 50
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
			cost += 200
		elif emptyCells == 2:
			# One piece in diagonal and attribute(s) in common with piece to be played.
			cost -= 50
	return cost

def costEstimate(state, player):
	""" Return heuristic cost for current state. """
	board = state.board
	transposed = zip(*board)
	rev = list(board)
	rev.reverse()
	opponentPiece = state.getPieceToPlay()
	# Evaluate board based on the current placed pieces and piece to be given to the opponent to play.
	cost = countRows(board, opponentPiece) + countRows(transposed, opponentPiece) + countDiagonal(board, opponentPiece) + countDiagonal(rev, opponentPiece)
	# Weight by depth. A winning state that happens in the fewest moves is preferred.
	return -player*cost