"""
This class is responsible for storing all the information about current state of the chess game. It will also be
responsible for determining valid moves at the current state. It will also keep a move log.
"""


class GameState():
    def __init__(self):
        # board is an 8*8 2d list . each element has 2 character.
        # first character means color. 2nd character piece name.
        # for example: bQ = black Queen
        # "--" represents empty space with no piece

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["--", "--", "--", "--", "--", "--", "--", "--", ],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.moveFunction = {'p': self.getPawnMoves, 'R': self.getRookeMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves, }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () #coordinates for the square where an passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastingRight.wks, self.currentCastingRight.bks, 
                                             self.currentCastingRight.wqs, self.currentCastingRight.bqs)]

    '''
    move a piece using move parameter. this will not work for pawn promotion, castling, en-passant
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"  # make blank in source
        self.board[move.endRow][move.endCol] = move.pieceMoved  # put piece in destination
        self.moveLog.append(move)  # log the move, so we can see history or undo move
        self.whiteToMove = not self.whiteToMove  # swap players

        # keep tracking of king in case of check
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        # empassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #capturing the pawn
        
        # update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #king side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #move the rock
                self.board[move.endRow][move.endCol+1] = '--' #erase old rook
            else: #queen side move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #move the rock
                self.board[move.endRow][move.endCol-2] = '--' #erase old rook

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # update castling rights - whenever it is a rock or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastingRight.wks, self.currentCastingRight.bks, 
                                             self.currentCastingRight.wqs, self.currentCastingRight.bqs))


    '''
      undo the last move
    '''
    def undoMove(self):
        if len(self.moveLog) > 0:  # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # swap players

            # keep tracking of king in case of check
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            #undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                # self.empassantPossible = (move.endRow, move.endCol)

            # undo a 2 square pawn advance
            # if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            #     self.enpassantPossible = ()
                
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # undo castling rights
            self.castleRightsLog.pop() #get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) # set the current rights to the last one in the list

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]     
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]     
                    self.board[move.endRow][move.endCol+1] = '--'
            
            #
            self.checkmate = False
            self.stalemate = False
    
    """
    Update the castle rights given the move
    """

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastingRight.wks = False
            self.currentCastingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastingRight.bks = False
            self.currentCastingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastingRight.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastingRight.bks = False

    """
    All moves considering checks
    """
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastingRight.wks, self.currentCastingRight.bks,
                                        self.currentCastingRight.wqs, self.currentCastingRight.bqs) #copy the current castling rights

        # 1. generate all possible moves
        moves = self.getAllPossibleMoves()

        # 2. for each move, make them
        for i in range(len(moves) - 1, -1, -1):     # when removing from a list fo backward through that list
            self.makeMove(moves[i])
            # 3. generate all opponent's move
            # 4. for each of your opponent's move, see if they attack your king.
            # 3 and 4
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            # 5. if they attack your king, then it's invalid move.
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastingRight = tempCastleRights
        return moves

    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # determine if the enemy attack r,c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove     # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)  # calls the appropriate move function based on piece
        return moves

    '''
    Get all the pawn moves at row,col and add these moves to the list
    gonna refactor this part of code later
    '''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn moves

            # 1 square pawn advance
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))

                # 2 square pawn advance
                if (self.board[r - 2][c] == "--") and (r == 6):
                    moves.append(Move((r, c), (r - 2, c), self.board))

            # capture left corner
            if (c-1 >= 0):
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            # capture right corner
            if (c+1 <= 7):
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:  # black pawn moves
            # 1 square pawn advance
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))

                # 2 square pawn advance
                if (self.board[r + 2][c] == "--") and (r == 1):
                    moves.append(Move((r, c), (r + 2, c), self.board))

            # capture left corner
            if (c-1 >= 0):
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))

            # capture right corner
            if (c+1 <= 7):
                if (self.board[r + 1][c + 1][0] == "w"):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

            # add pawn promotion later

    '''
    4 direction ei jete pare
    loop for each direction:
       left=>
           loop for each cell
               first cell=> check piece and take decision
               adjacent cell theke count shuru hobe. adjacent invalid hole ar samne jete parbena
               so loop break
    this is common for both rooke and bishop. only difference one goes straight another diagonal.
    so after deciding direction just use this function.
    '''

    def getCommonMoves(self, directions, r, c, moves):
        enemyColor = "b" if self.whiteToMove else "w"  # defining enemy color
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:
                    break

    def getRookeMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        self.getCommonMoves(directions, r, c, moves)

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonal
        self.getCommonMoves(directions, r, c, moves)

    def getKingAndKnightMoves(self, directions, r, c, moves):
        allyColor = "w" if self.whiteToMove else "b"
        for m in directions:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKnightMoves(self, r, c, moves):
        directions = ((2, -1), (2, 1), (-2, 1), (-2, -1), (1, -2), (1, 2), (-1, -2), (-1, 2))
        self.getKingAndKnightMoves(directions, r, c, moves)

    def getKingMoves(self, r, c, moves):
        # kingMoves = ((0, -1), (0, 1), (1, 0), (-1, 0), (-1, -1), (1, 1), (1, -1), (-1, 1))
        # allyColor = "w" if self.whiteToMove else "b"
        # for i in range(8):
        #     endRow = r + kingMoves[i][0]
        #     endCol = c + kingMoves[i][1]
        # if 0 <= endRow < 8 and 0 <= endCol < 8:
        #     endPiece = self.board[endRow][endCol]
        #     if endPiece[0] != allyColor: # not an ally piece (empty or enemy piece) 
        #         moves.append(Move((r, c), (endRow, endCol), self.board))
        # self.getCastleMoves(r, c, moves)
        
        directions = ((0, -1), (0, 1), (1, 0), (-1, 0), (-1, -1), (1, 1), (1, -1), (-1, 1))
        self.getKingAndKnightMoves(directions, r, c, moves)
    
    """
    Generate all valid castle moves for the king at (r,c) and add them to the list of moves
    """
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #can't castle while we are in check
        if (self.whiteToMove and self.currentCastingRight.wks) or (not self.whiteToMove and self.currentCastingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastingRight.wqs) or (not self.whiteToMove and self.currentCastingRight.bqs):
            self.getKingSideCastleMoves(r, c, moves)
    
    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))

    def getQueenSideCastleMoves(self, r, c, moves):
         if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookeMoves(r, c, moves)




class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # maps keys to value
    # key : value
    # normally chess e vertical e 0-7 numbering kora. starting from white.
    # horizontal e a-h. called files. our board orders are not same. hence, mapping.
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}  # mapping dictionary
    rowsToRanks = {v: k for k, v in ranksToRows.items()}  # reverse a dictionary

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}  # mapping dictionary
    colsToFiles = {v: k for k, v in filesToCols.items()}  # reverse a dictionary

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        #en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    # source Destination of current move. example : d2d4
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
