"""
This is our main driver file. It will be responsible for holding user input and display the current GameState Object
"""

import pygame as p


import ChessEngine, SmartMoveFinder
# from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8  # dimension of chess board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animation
IMAGES = {}

'''
Initialise a global dictionary of images. This will be called exactly once in the main.
'''


def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        # images loading with scaling
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

    # Note: we can access an image by saying 'IMAGES['WP']'


'''
The main driver of our code. This will handle user input and updating the graphics
'''


def main():
    p.init()
    p.display.set_caption("Chess with AI")
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()

    validMoves = gs.getValidMoves()
    moveMade = False    # flag variable for when a move is made
    animate = False # flag variable for when we should animate a move 
    loadImages()  # only do this once. before the while loop

    running = True
    sqSelected = ()  # no squared selected initially. keep track of the last click of user. (tuple: (row,col))
    playerClicks = []  # keep track of player clicks (two tuple: ((6,4),(4,4))
    gameOver = False
    playerOne = False #If a Human is playing white, then this will be true.
    playerTwo = False #Same as above but for black
    
    while running:  # game started
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for event in p.event.get():
            if event.type == p.QUIT:  # cross clicked
                running = False  # quit game

            # mouse click
            elif event.type == p.MOUSEBUTTONDOWN:  # left or right click of mouse
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col):  # user clicked the same square twice
                        sqSelected = ()  # deselecting user click
                        playerClicks = []  # clear user clicks

                    else:  # valid click
                        sqSelected = (row, col)  # selecting user click
                        playerClicks.append(sqSelected)  # append for both first and second click

                    if len(playerClicks) == 2:  # after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                # print(move.pieceMoved)
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                                txtMove = "White's turn" if gs.whiteToMove else "Black's turn"
                                print(txtMove)
                        if not moveMade:
                            playerClicks = [sqSelected]

            # undo move
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if event.key == p.K_r: #reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Checkmate! Black wins.')
            else:
                drawText(screen, 'Checkmate! White wins.')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate!')

        # UI
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight square selected and move for piece selected
'''

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('yellow'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


'''
Responsible for all the graphics within a current game state
'''

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw square on boards
    highlightSquares(screen, gs, validMoves, sqSelected)
    # add in piece highlighting and move suggestions
    drawPieces(screen, gs.board)


'''
Draw the squares on the board. The top left corner is always light.
'''
def drawBoard(screen):
    global colors
    light_gray = (115, 149, 82)
    beige = (235, 236, 208)
    colors = [p.Color(beige), p.Color(light_gray)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSquare = 10 #frame to move one square
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            p.display.flip()
            clock.tick(60)
    
def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Grey'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

main()
