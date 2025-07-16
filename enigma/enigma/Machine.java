package enigma;
import java.util.HashMap;
import java.util.Collection;
import static enigma.EnigmaException.*;

/** Class that represents a complete enigma machine.
 *  @author Elijah G. Jacob
 */
class Machine<Msg> {
    /**
     * Alphabet of my rotors.
     */
    private final Alphabet _alphabet;

    /**
     * The number of rotors.
     */

    private int _numRotors;
    /**
     * The number of pawls.
     */
    private int _pawls;
    /**
     * The rotors in iterable form.
     */
    private Rotor [] _allRotors;
    /**
     * The plugboard permutations. */
    private Permutation _plugboard;
    /**
     * The converted message. */
    private int convertedmsg1;
    /**
     * The initial message . */
    private String firstmsg;
    /**
     * The utilized rotors. */
    private Rotor [] _usedRotors;
    /** A hashmap for the  rotors. */
    private static HashMap<String, Rotor> rotorMap = new HashMap<>();


    /**
     * A new Enigma machine with alphabet ALPHA, 1 < NUMROTORS rotor slots,
     * and 0 <= PAWLS < NUMROTORS pawls.  ALLROTORS contains all the
     * available rotors.
     */
    Machine(Alphabet alpha, int numRotors, int pawls,
            Collection<Rotor> allRotors) {
        _alphabet = alpha;
        _numRotors = numRotors;
        _pawls = pawls;
        _allRotors = allRotors.toArray(new Rotor[0]);
        _usedRotors = new Rotor[numRotors];
        for (int x = 0; x < numRotors; x++) {
            rotorMap.put(_allRotors[x].name(), _allRotors[x]);
        }
    }

    /**
     * Return the number of rotor slots I have.
     */
    int numRotors() {
        return _numRotors;
    }

    int numPawls() {
        return _pawls;
    }


    Alphabet alphabet() {
        return _alphabet;
    }

    boolean rotorFlag() {
        int reflector = 0;
        int rotating = 0;
        int still = 0;
        boolean flag = true;

        if (_usedRotors.length != _numRotors) {
            throw new EnigmaException("Incorrect number of rotors");
        }

        for (int x = 0; x < _usedRotors.length; x++) {
            for (int y = 0; y < _usedRotors.length; y++) {
                if (_usedRotors[x] == _usedRotors[y] && x != y) {
                    throw error("Rotors are duplicate");
                }
            }
        }
        for (int x = 0; x < _usedRotors.length; x++) {
            if (_usedRotors[x].reflecting()) {
                reflector++;
            }
            if (_usedRotors[x].rotates()) {
                rotating++;
            }
        }
        if (reflector != 1) {
            throw error("Incorrect number of reflectors");
        }
        if (rotating != numPawls()) {
            throw error("Incorrect number of moving rotors");
        }
        return flag;
    }

    void insertRotors(String[] rotors) {
        for (int x = 0; x < numRotors(); x++) {
            _usedRotors[x] = rotorMap.get(rotors[x]);
        }
        rotorFlag();
        for (int x = 0; x < _usedRotors.length; x++) {
            if (_usedRotors[x] == null) {
                throw new EnigmaException("Error: Check the input file");
            }
            for (x = 0; x < rotors.length; x++) {
                for (Object current : _allRotors) {
                    String uppername = ((Rotor) current).name().toUpperCase();
                    if (rotors[x].equals(uppername)) {
                        _usedRotors[x] = (Rotor) current;
                    }
                }
            }
        }
    }

    void setRotors(String setting) {
        for (int x = 0; x < numRotors() - 1; x++) {
            _usedRotors[x + 1].set(setting.charAt(x));
        }
    }

    Permutation plugboard() {
        return _plugboard;
    }

    void setPlugboard(Permutation plugboard) {
        _plugboard = plugboard;
    }


    Rotor getRotor(int k) {
        return _usedRotors[k];
    }


    int convert(int c) {
        advanceRotors();
        if (Main.verbose()) {
            System.err.printf("[");
            for (int r = 1; r < numRotors(); r += 1) {
                System.err.printf("%c",
                        alphabet().toChar(getRotor(r).setting()));
            }
            System.err.printf("] %c -> ", alphabet().toChar(c));
        }
        c = plugboard().permute(c);
        if (Main.verbose()) {
            System.err.printf("%c -> ", alphabet().toChar(c));
        }
        c = applyRotors(c);
        c = plugboard().permute(c);
        if (Main.verbose()) {
            System.err.printf("%c%n", alphabet().toChar(c));
        }
        return c;
    }

    private int applyRotors(int c) {
        int x;
        for (x = _usedRotors.length - 1; x >= 0; x--) {
            c = _usedRotors[x].convertForward(c);
        }
        for (x = 0; x <= _usedRotors.length - 1; x++) {
            c = _usedRotors[x].convertBackward(c);
        }
        return c;
    }

    String convert(String msg) {
        String convertedmsg = " ";
        char [] charArray = msg.toCharArray();
        for (int x = 0; x < charArray.length; x++) {
            int alphabetlett = _alphabet.toInt(charArray[x]);
            this.convertedmsg1 += _alphabet.toChar(convert(alphabetlett));
        }
        return convertedmsg;
    }

    private void advanceRotors() {
        boolean [] advance =  new boolean [_usedRotors.length];
        advance [_usedRotors.length - 1] = true;
        for (int x = 1; x < _usedRotors.length - 1; x++) {
            if (_usedRotors[x + 1].atNotch()) {
                advance [x] = true;
            }
        }
        for (int x = 2; x < _usedRotors.length - 1; x++) {
            if (_usedRotors[x].atNotch() &&  _usedRotors[x - 1].rotates()) {
                advance [x] = true;
            }
        }
        for (int x = 0; x < _usedRotors.length; x++) {
            if (advance[x]) {
                _usedRotors[x].advance();
            }
        }
    }
}


