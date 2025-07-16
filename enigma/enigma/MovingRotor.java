package enigma;

import static enigma.EnigmaException.*;

/** Class that represents a rotating rotor in the enigma machine.
 *  @author P.N.Hilfinger
 */
class MovingRotor extends Rotor {

    /** A var to init notches.
     */
    private String _notches;
    /** A var to init settings.
     */
    private int _setting;
    /** A var of obj rotor.
     */
    private Rotor rotor;

    /** A rotor named NAME whose permutation in its default setting is
     *  PERM, and whose notches are at the positions indicated in NOTCHES.
     *  The Rotor is initially in its 0 setting (first character of its
     *  alphabet).
     */
    MovingRotor(String name, Permutation perm, String notches) {
        super(name, perm);
        _notches = notches;
    }
    /** Advances the rotor by one.
     */
    @Override
    void advance() {
        int move = permutation().wrap(_setting + 1);
        set(move);
    }

    /** Rotates the rotor by one.
     */
    @Override
    boolean rotates() {
        return true;
    }

    /** Checks if the rotor is at a notch.
     */
    @Override
    boolean atNotch() {
        String c = Character.toString(alphabet().toChar(_setting));
        if (_notches.contains(c)) {
            return true;
        }
        return false;
    }

}
