import random

pieceScore = {"K" : 0, "Q" : 9, "R" : 5, "B" : 3, "N" : 3, "p" : 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


'''
Min Max without recursive call
'''

# def findBestMove(gs, validMoves):
#     turnMultiplier = 1 if gs.whiteToMove else -1
#     opponentsMinMaxScore = CHECKMATE
#     bestPlayerMove = None
#     random.shuffle(validMoves)

#     for playerMove in validMoves:
#         gs.makeMove(playerMove)
#         opponanetsMoves = gs.getValidMoves()
#         if gs.stalemate:
#             opponanetMaxScore = STALEMATE
#         elif gs.checkmate:
#             opponanetMaxScore = -CHECKMATE
#         else:
#             opponanetMaxScore = -CHECKMATE

#             for opponanetsMove in opponanetsMoves:
#                 gs.makeMove(opponanetsMove)
#                 gs.getValidMoves()
#                 if gs.checkmate:
#                     score = CHECKMATE
#                 elif gs.stalemate:
#                     score = STALEMATE
#                 else:
#                     score = -turnMultiplier * scoreMaterial(gs.board)

#                 if score > opponanetMaxScore:
#                     opponanetMaxScore = score
#                 gs.undoMove()
#         if opponentsMinMaxScore > opponanetMaxScore:
#             opponentsMinMaxScore = opponanetMaxScore
#             bestPlayerMove = playerMove
#         gs.undoMove()
#     return bestPlayerMove

'''
Helper method to make the first recursive call
'''

def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    # findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    # findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    counter = 0
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counter)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMove = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMove, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMove = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMove, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMove = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMove, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth==DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    # move ordering 
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMove = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMove, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth==DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore>alpha: #purining happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore
    
    

'''
A positive score is good for white, negative for black
'''

def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score  



'''
Score the board based on material
'''
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score

