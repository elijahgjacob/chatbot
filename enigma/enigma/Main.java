package enigma;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Scanner;
import ucb.util.CommandArgs;

import static enigma.EnigmaException.*;

/** Enigma simulator.
 *  @author P.N.Hilfinger
 */
public final class Main {

    /** Process a sequence of encryptions and decryptions, as
     *  specified by ARGS, where 1 <= ARGS.length <= 3.
     *  ARGS[0] is the name of a configuration file.
     *  ARGS[1] is optional; when present, it names an input file
     *  containing messages.  Otherwise, input comes from the standard
     *  input.  ARGS[2] is optional; when present, it names an output
     *  file for processed messages.  Otherwise, output goes to the
     *  standard output. Exits normally if there are no errors in the input;
     *  otherwise with code 1. */
    public static void main(String... args) {
        try {
            CommandArgs options =
                new CommandArgs("--verbose --=(.*){1,3}", args);
            if (!options.ok()) {
                throw error("Usage: java enigma.Main [--verbose] "
                            + "[INPUT [OUTPUT]]");
            }

            _verbose = options.contains("--verbose");
            new Main(options.get("--")).process();
            return;
        } catch (EnigmaException excp) {
            System.err.printf("Error: %s%n", excp.getMessage());
        }
        System.exit(1);
    }

    /** Open the necessary files for non-option arguments ARGS (see comment
      *  on main). */
    Main(List<String> args) {
        _config = getInput(args.get(0));

        if (args.size() > 1) {
            _input = getInput(args.get(1));
        } else {
            _input = new Scanner(System.in);
        }

        if (args.size() > 2) {
            _output = getOutput(args.get(2));
        } else {
            _output = System.out;
        }
    }

    /** Return a Scanner reading from the file named NAME. */
    private Scanner getInput(String name) {
        try {
            return new Scanner(new File(name));
        } catch (IOException excp) {
            throw error("could not open %s", name);
        }
    }

    /** Return a PrintStream writing to the file named NAME. */
    private PrintStream getOutput(String name) {
        try {
            return new PrintStream(new File(name));
        } catch (IOException excp) {
            throw error("could not open %s", name);
        }
    }

    /** Configure an Enigma machine from the contents of configuration
     *  file _config and apply it to the messages in _input, sending the
     *  results to _output. */
    private void process() {
        Machine enigma = readConfig();
        String e = "Rotors not valid";
        String a = " not in alphabet";
        while (_input.hasNextLine()) {
            String nextLine = _input.nextLine();
            if (nextLine.contains("*")) {
                setUp(enigma, nextLine);
            } else {
                for (int x = 0; x < nextLine.length(); x++) {
                    if (!_alphabet.contains(nextLine.charAt(x))) {
                        if (nextLine.charAt(x) != ' ') {
                            throw new EnigmaException(nextLine.charAt(x) + a);
                        }
                    }
                }

                if (!enigma.rotorFlag()) {
                    throw new EnigmaException(e);
                }
                printMessageLine(enigma.convert(nextLine));
            }
        }
    }

    /** Return an Enigma machine configured from the contents of configuration
     *  file _config. */
    private Machine readConfig() {
        try {
            boolean flag = false;
            _alphabet = new Alphabet(_config.next());
            String numRotors = _config.next();
            String numPawls = _config.next();
            int rotorcount = Integer.parseInt(numRotors);
            int pawlcount = Integer.parseInt(numPawls);
            Collection<Rotor> allRotors = new ArrayList<>();
            if (pawlcount + 1 < rotorcount) {
                flag = true;
                throw new EnigmaException("Err: rotor and pawl in conf. file");
            }
            if (!_config.hasNext()) {
                flag = true;
                throw new EnigmaException("No Rotors available");
            }
            if (allRotors.size() < pawlcount) {
                flag = true;
                throw new EnigmaException("You need more rotors");
            }
            if (!flag) {
                allRotors.add(readRotor());
            }
            return new Machine(_alphabet, rotorcount, pawlcount, allRotors);
        } catch (NoSuchElementException excp) {
            throw error("configuration file truncated");
        }
    }

    /** Return a rotor, reading its description from _config. */
    private Rotor readRotor() {
        try {
            String rotorName = _config.next();
            String rotorConf = _config.next();
            String cycles = "";
            while (_config.hasNext()) {
                this._next = _config.next();
            }
            Permutation perm = new Permutation(cycles, _alphabet);
            if (rotorConf.startsWith("M")) {
                String notches = rotorConf.substring(1);
                return new MovingRotor(rotorName, perm, notches);
            } else if (rotorConf.startsWith("N")) {
                return new FixedRotor(rotorName, perm);
            } else {
                return new Reflector(rotorName, perm);
            }
        } catch (NoSuchElementException excp) {
            throw error("bad rotor description");
        }
    }

    private void charalpha(String str) {
        for (int x = 0; x < str.length(); x++) {
            if (!(_alphabet.contains(str.charAt(x)))) {
                throw new EnigmaException(str + "Chars in cycle but not alpha");
            }
        }
    }


    private void isInvalid(String str) {
        if (!str.equals("*")) {
            throw new EnigmaException("Incorrect first line");
        }
    }

    private void plgCheck(String str) {
        if (!str.matches("\\(.+\\)")) {
            throw new EnigmaException("Check plugboard settings.");
        }
    }

    /** Set M according to the specification given on SETTINGS,
     *  which must have the format specified in the assignment. */
    private void setUp(Machine M, String settings) {
        String[] spltInpt = settings.split("\\s+");

        isInvalid(spltInpt[0]);

        String[] rotorLst = new String[M.numRotors()];

        for (int i = 0; i < M.numRotors(); i++) {
            rotorLst[i] = spltInpt[i + 1];
        }

        M.insertRotors(rotorLst);
        charalpha(spltInpt[M.numRotors() + 1]);
        M.setRotors(spltInpt[M.numRotors() + 1]);

        Permutation plugboard;

        String swaps = "";
        for (int i = M.numRotors(); i < spltInpt.length; i++) {
            charalpha(spltInpt[i].substring(1, spltInpt[i].length() - 1));
            plgCheck(spltInpt[i]);
            swaps += spltInpt[i];
        }
        plugboard = new Permutation(swaps, _alphabet);

        M.setPlugboard(plugboard);
    }

    /** Return true iff verbose option specified. */
    static boolean verbose() {
        return _verbose;
    }

    /** Print MSG in groups of five (except that the last group may
     *  have fewer letters). */
    private void printMessageLine(String msg) {
        int strlen = msg.length();
        int i = 0;
        for (int x = 0; x < strlen / 5 + 1; x++) {
            for (int y = 0; y < 5; y++) {
                if (i == msg.length()) {
                    break;
                }
                System.out.println(msg.charAt(i));
                i++;
            }
            System.out.println(" ");
        }
    }

    /** Alphabet used in this machine. */
    private Alphabet _alphabet;

    /** Source of input messages. */
    private Scanner _input;

    /** Source of machine configuration. */
    private Scanner _config;

    /** Next value of _input to be accessed across classes. */
    private String _next;

    /** File for encoded/decoded messages. */
    private PrintStream _output;

    /** True if --verbose specified. */
    private static boolean _verbose;

    /** List to show all Rotors. */
    private ArrayList<Rotor> _allRotors;

}
