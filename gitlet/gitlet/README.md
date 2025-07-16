# Gitlet: A Tiny Version-Control System

Gitlet is a simplified version-control system inspired by Git, implemented in Java. It allows you to manage file versions, track changes, and collaborate on projects using a command-line interface.

## Features

- **Initialization (`init`):** Initializes a new Gitlet version-control system in the current directory.
- **Add (`add <file>`):** Adds a file to the staging area for the next commit.
- **Commit (`commit <message>`):** Commits the current changes with a message.
- **Checkout (`checkout`):** Restores files or switches branches based on the provided arguments.
- **Remove (`rm <file>`):** Removes a file from the staging area or the working directory.
- **Branch Management (`branch <branch name>`, `rm-branch <branch name>`):** Creates and deletes branches.
- **Logging (`log`, `global-log`):** Displays the commit history.
- **Status (`status`):** Displays the current status of the repository.
- **Find (`find <message>`):** Finds commits by their commit messages.
- **Reset (`reset <commit ID>`):** Resets the current branch to a specified commit.
- **Merge (`merge <branch name>`):** Merges the specified branch into the current branch.

## Requirements

- Java Development Kit (JDK) version 8 or higher.
- A terminal or command prompt to run Gitlet commands.

## How to Run

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/your-username/gitlet.git
   cd gitlet
   ```

2. **Compile the Program:**
   ```sh
   javac gitlet/Main.java
   ```

3. **Run the Program:**
   ```sh
   java gitlet.Main <command> [operands]
   ```

## Usage

### Commands

- **`init`**: Initializes a new Gitlet version-control system in the current directory.
    ```sh
    java gitlet.Main init
    ```

- **`add <file>`**: Stages the specified file for the next commit.
    ```sh
    java gitlet.Main add <file>
    ```

- **`commit <message>`**: Commits the current changes with the given message.
    ```sh
    java gitlet.Main commit "Your commit message"
    ```

- **`checkout [-- <file> | <branch name> | <commit ID> -- <file>]`**: Restores files or switches branches.
    ```sh
    java gitlet.Main checkout -- <file>
    java gitlet.Main checkout <branch name>
    java gitlet.Main checkout <commit ID> -- <file>
    ```

- **`rm <file>`**: Removes a file from the staging area or the working directory.
    ```sh
    java gitlet.Main rm <file>
    ```

- **`log`**: Displays the commit history of the current branch.
    ```sh
    java gitlet.Main log
    ```

- **`status`**: Displays the status of the repository.
    ```sh
    java gitlet.Main status
    ```

- **`global-log`**: Displays the commit history of all branches.
    ```sh
    java gitlet.Main global-log
    ```

- **`find <message>`**: Finds commits by their commit messages.
    ```sh
    java gitlet.Main find "commit message"
    ```

- **`reset <commit ID>`**: Resets the current branch to the specified commit.
    ```sh
    java gitlet.Main reset <commit ID>
    ```

- **`branch <branch name>`**: Creates a new branch with the given name.
    ```sh
    java gitlet.Main branch <branch name>
    ```

- **`rm-branch <branch name>`**: Deletes the branch with the given name.
    ```sh
    java gitlet.Main rm-branch <branch name>
    ```

- **`merge <branch name>`**: Merges the specified branch into the current branch.
    ```sh
    java gitlet.Main merge <branch name>
    ```

### Example Usage

```sh
java gitlet.Main init
java gitlet.Main add myfile.txt
java gitlet.Main commit "Initial commit"
java gitlet.Main log
```

## Developer Information

- **Author:** Elijah G. Jacob

## Contributing

This project is an educational tool and is not intended for production use. Contributions are welcome, but please get in touch before making any major changes.

## License

This code is proprietary. Do not distribute this or any derivative work without explicit permission from the author.

## Contact

For questions or suggestions, contact Elijah G. Jacob.
```

Feel free to copy this content, and it will maintain the markdown formatting.
