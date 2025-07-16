package ataxx;

import java.util.ArrayList;
import java.util.Random;

import static ataxx.PieceColor.*;
import static java.lang.Math.max;
import static java.lang.Math.min;


/** A Player that computes its own moves.
 *  @author Paul N. Hilfinger
 */
class AI extends Player {

    /** Maximum minimax search depth before going to static evaluation. */
    private static final int MAX_DEPTH = 4;
    /** A position magnitude indicating a win (for red if positive, blue
     *  if negative). */
    private static final int WINNING_VALUE = Integer.MAX_VALUE - 20;
    /** A magnitude greater than a normal value. */
    private static final int INFTY = Integer.MAX_VALUE;

    final int alpha = Integer.MIN_VALUE;

    final int beta = Integer.MAX_VALUE;


    /** A new AI for GAME that will play MYCOLOR. SEED is used to initialize
     *  a random-number generator for use in move computations.  Identical
     *  seeds produce identical behaviour. */
    AI(Game game, PieceColor myColor, long seed) {
        super(game, myColor);
        _random = new Random(seed);
    }

    @Override
    boolean isAuto() {
        return true;
    }

    @Override
    String getMove() {
        if (!getBoard().canMove(myColor())) {
            game().reportMove(Move.pass(), myColor());
            return "-";
        }
        Main.startTiming();
        Move move = findMove();
        Main.endTiming();
        game().reportMove(move, myColor());
        return move.toString();
    }

    /** Return a move for me from the current position, assuming there
     *  is a move. */
    private Move findMove() {
        Board b = new Board(getBoard());
        _lastFoundMove = null;
        if (myColor() == RED) {
            minMax(b, MAX_DEPTH, true, 1, -INFTY, INFTY);
        } else {
            minMax(b, MAX_DEPTH, true, -1, -INFTY, INFTY);
        }
        return _lastFoundMove;
    }

    /** The move found by the last call to the findMove method
     *  above. */
    private Move _lastFoundMove;

    /** Find a move from position BOARD and return its value, recording
     *  the move found in _foundMove iff SAVEMOVE. The move
     *  should have maximal value or have value > BETA if SENSE==1,
     *  and minimal value or value < ALPHA if SENSE==-1. Searches up to
     *  DEPTH levels.  Searching at level 0 simply returns a static estimate
     *  of the board value and does not set _foundMove. If the game is over
     *  on BOARD, does not set _foundMove. */
    private int minMax(Board board, int depth, boolean saveMove, int sense,
                       int alpha, int beta) {
        /* We use WINNING_VALUE + depth as the winning value to favor
         * wins that happen sooner rather than later (depth is larger the
         * fewer moves have been made. */


        alpha = Integer.MIN_VALUE;
        beta = Integer.MAX_VALUE;
        ArrayList<Move> movesArr = new ArrayList<>();
        for (int x = 0; x < board.length(); x++) {
            PieceColor pc = board.whoseMove();
            if (board.get(x) == pc) {
                for (int colsaway = -1; colsaway < 2; colsaway++) {
                    for (int rowsaway = -1; rowsaway < 2; rowsaway++) {
                        int toInd = board.neighbor(x, colsaway, rowsaway);
                        if (board.get(toInd) == EMPTY) {
                            char c0 = board.reverseindexc(x);
                            char r0 = board.reverseindexr(x);
                            char c1 = board.reverseindexc(toInd);
                            char r1 = board.reverseindexr(toInd);
                            if (board.legalMove(Move.move(c0, r0, c1, r1))) {
                                movesArr.add(Move.move(c0, r0, c1, r1));
                            }
                        }
                    }
                }
            }
        }

        if (depth == 0 || board.getWinner() != null) {
            return staticScore(board, WINNING_VALUE + depth);
        }

        for (int x = 0; x < movesArr.size(); x++) {
            board.makeMove(movesArr.get(x));
            if (sense == 1) {
                int response = minMax(board, depth - 1, false, 1, alpha, beta);
                alpha = max(alpha, response);
                if (saveMove) {
                    _lastFoundMove = movesArr.get(x);
                }
            } else {
                int response = minMax(board, depth - 1, false, -1, alpha, beta);
                beta = min(beta, response);
                if (saveMove) {
                    _lastFoundMove = movesArr.get(x);
                }
            }
            board.undo();
        }
        return staticScore(board, WINNING_VALUE + depth);
    }


    /** Return a heuristic value for BOARD.  This value is +- WINNINGVALUE in
     *  won positions, and 0 for ties. */
    private int staticScore(Board board, int winningValue) {
        PieceColor winner = board.getWinner();
        if (winner != null) {
            return switch (winner) {
                case RED -> winningValue;
                case BLUE -> -winningValue;
                default -> 0;
            };
        }
        return board.bluePieces() - board.redPieces();
    }

    /** Pseudo-random number generator for move computation. */
    private Random _random = new Random();
}
