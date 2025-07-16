package enigma;

/** Represents a permutation of a range of integers starting at 0 corresponding
 *  to the characters of an alphabet.
 *  @author Elijah G. Jacob
 */
class Permutation {
    /** A var to init the alphabet.
     */
    private Alphabet _alphabet;
    /** A var to init the cycle.
     */
    private String _cycles;

    Permutation(String cycles, Alphabet alphabet) {
        _alphabet = alphabet;
        _cycles = cycles;
    }

    /**
     * Add the cycle c0->c1->...->cm->c0 to the permutation, where CYCLE is
     * c0c1...cm.
     */
    private void addCycle(String cycle) {
        _cycles += " " + cycle;
    }

    /**
     * Return the value of P modulo the size of this permutation.
     */
    final int wrap(int p) {
        int r = p % size();
        if (r < 0) {
            r += size();
        }
        return r;
    }

    /**
     * Returns the size of the alphabet I permute.
     */
    int size() {
        return _alphabet.size();
    }

    /**
     * Return the result of applying this permutation to P modulo the
     * alphabet size.
     */
    int permute(int p) {
        String[] cyclearray = _cycles.split("\\) *\\(");
        char pchar = _alphabet.toChar(wrap(p));
        char base = 0;
        for (int x = 0; x < cyclearray.length; x++) {
            cyclearray[x] = cyclearray[x].replaceAll("\\(", "");
            cyclearray[x] = cyclearray[x].replaceAll("\\)", "");
            for (int y = 0; y < cyclearray[x].length(); y++) {
                if (_alphabet.toInt(cyclearray[x].charAt(y)) == wrap(p)) {
                    int cyclelen =  cyclearray[x].length();
                    base = cyclearray[x].charAt(Rotor.rem((y + 1), cyclelen));
                    return _alphabet.toInt(base);
                }
            }
        }
        return p;
    }
    /**
     * Return the result of applying the inverse of this permutation
     * to  C modulo the alphabet size.
     */
    int invert(int c) {
        String[] cyclearray = _cycles.split("\\) *\\(");
        char cchar = _alphabet.toChar(wrap(c));
        char base;
        for (int x = 0; x < cyclearray.length; x++) {
            cyclearray[x] = cyclearray[x].replaceAll("\\(", "");
            cyclearray[x] = cyclearray[x].replaceAll("\\)", "");
            for (int y = 0; y < cyclearray[x].length(); y++) {
                if (cyclearray[x].charAt(y) == cchar) {
                    int cyclelen =  cyclearray[x].length();
                    base = cyclearray[x].charAt(Rotor.rem((y - 1), cyclelen));
                    if (_alphabet.toInt(base) == -1) {
                        return c;
                    }
                    return _alphabet.toInt(base);
                }
            }
        }
        return c;
    }


    /**
     * Return the result of applying this permutation to the index of P
     * in ALPHABET, and converting the result to a character of ALPHABET.
     */
    char permute(char p) {
        int x = _alphabet.toInt(p);
        if (x == -1) {
            return p;
        } else {
            x = permute(x);
            return _alphabet.toChar(x);
        }
    }

    /** Return the result of applying the inverse of this permutation to C. */
    char invert(char c) {
        int y = alphabet().toInt(c);
        if (y == -1) {
            return c;
        } else {
            y = invert(y);
            return _alphabet.toChar(y);
        }
    }

    /** Return the alphabet used to initialize this Permutation. */
    Alphabet alphabet() {
        return _alphabet;
    }

    /** Return true iff this permutation is a derangement (i.e., a
     *  permutation for which no value maps to itself). */
    boolean derangement() {
        for (int i = 0; i < alphabet().size(); i++) {
            char c = alphabet().toChar(i);
            if (c == permute(c)) {
                return false;
            }
        }
        return true;
    }


}
