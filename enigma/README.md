# Enigma Simulator

This project is a Java implementation of an Enigma machine simulator. The Enigma machine was used for encryption and decryption of messages, most famously by the German military during World War II. This simulator processes a sequence of encryptions and decryptions specified by input arguments, reading configurations from a file and optionally reading messages from a file or standard input.

## Usage

To run the Enigma simulator, use the following command:

```bash
java enigma.Main [--verbose] CONFIG_FILE [INPUT_FILE] [OUTPUT_FILE]
```

### Arguments

- `CONFIG_FILE`: The name of the configuration file that defines the Enigma machine's settings, including rotors, reflectors, and the plugboard.
- `INPUT_FILE` (optional): The name of the input file containing messages to be processed. If not provided, the simulator reads from the standard input.
- `OUTPUT_FILE` (optional): The name of the output file where the processed messages are written. If not provided, the simulator writes to the standard output.
- `--verbose` (optional): Enables verbose mode, which provides detailed logging of the simulator's internal operations.

## Configuration File Format

The configuration file must specify the following:

1. **Alphabet**: A string representing the characters used in the machine.
2. **Number of Rotors**: An integer representing the total number of rotors in the machine.
3. **Number of Pawls**: An integer representing the number of pawls (moving rotors).
4. **Rotor Descriptions**: Each rotor's name, type (`M`, `N`, or reflector type), and cycles.

### Example Configuration File

```
ABCDEFGHIJKLMNOPQRSTUVWXYZ
5
3
I MQ (AJDKSIRUXBLHWTMCQGZNPYFVOE)
II MF (BDFHJLCPRTXVZNYEIWGAKMUSQO)
III MN (EKMFLGDQVZNTOWYHXUSPAIBRCJ)
B N (YRUHQSLDPXNGOKMIEBFZCWVJAT)
C N (FVPJIAOYEDRZXWGCTKUQSBNMHL)
```

## Methods Overview

- **`main(String... args)`**: The entry point that processes the input arguments, initializes the necessary files, and starts the encryption or decryption process.
- **`process()`**: Configures the Enigma machine based on the configuration file and applies it to the input messages.
- **`readConfig()`**: Reads the machine configuration from the file and sets up the rotors and plugboard.
- **`readRotor()`**: Reads and constructs each rotor from the configuration.
- **`setUp(Machine M, String settings)`**: Sets up the machine with the specified rotor order, initial rotor positions, and plugboard settings.
- **`printMessageLine(String msg)`**: Formats and prints the encrypted or decrypted message in groups of five characters.

## Exception Handling

The simulator uses custom exception handling to manage errors related to file input, configuration parsing, and machine setup. Errors are displayed with a meaningful message, and the simulator exits with code `1` in case of an error.

## Example Usage

### Encrypting a Message

To encrypt a message using the configuration in `config.txt` and an input file `input.txt`, and save the result in `output.txt`, use:

```bash
java enigma.Main config.txt input.txt output.txt
```

### Verbose Mode

To enable verbose mode for detailed logging:

```bash
java enigma.Main --verbose config.txt input.txt output.txt
```

### Reading from Standard Input and Output

If you want to read the message from standard input and output the result to the console:

```bash
java enigma.Main config.txt
```

## Contributing

Feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
