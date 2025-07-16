package gitlet;

import java.io.IOException;

/**
 * Driver class for Gitlet, the tiny stupid version-control system.
 *
 * @author Elijah G. Jacob
 */
public class Main {
    /**
     * Usage: java gitlet.Main ARGS, where ARGS contains
     * <COMMAND> <OPERAND> ....
     */

    public static void main(String... args)
            throws IOException, ClassNotFoundException, IndexOutOfBoundsException {
        if (args.length == 0) {
            System.out.println("Please enter a command.");
            System.exit(0);
        }
        String first = args[0];
        Commands c = new Commands();
        switch (first) {
            case "init":
                if (args.length > 1) {
                    System.out.println("Please enter the "
                            + "right amount of arguments.");
                    System.exit(0);
                } else if (c.saveInit()) {
                    System.out.println("A Gitlet version-control system already"
                            + "exists in the current directory.");
                    System.exit(0);
                }
                c.init();
                break;
            case "add":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
                if (args.length != 2) {
                    System.out.println("Please enter the "
                            + "right amount of arguments");
                    System.exit(0);
                }
                if (!c.add(args[1])) {
                    System.out.println("File does not exist.");
                    System.exit(0);
                }
                break;
            case "commit":
                if (!c.saveInit()) {
                    System.out.println("Directory not "
                            + "initialized");
                    System.exit(0);
                }
                if (args.length == 1 || args[1].isEmpty()) {
                    System.out.println("Please enter a commit "
                            + "message.");
                    System.exit(0);
                }
                if (args.length > 2) {
                    System.out.println("Please enter the right amount "
                            + "of arguments");
                    System.exit(0);
                }
                String message = args[1];
                c.commit(message);
                break;
            case "checkout":
                if (args.length == 3 && args[1].equals("--")) {
                    if (!c.saveInit()) {
                        System.out.println("Directory not initialized");
                        System.exit(0);
                    }
                    String checkoutFN = args[2];
                    c.checkout1(checkoutFN);
                } else if (args.length == 4 && args[2].equals("--")) {
                    if (!c.saveInit()) {
                        System.out.println("Directory not initialized");
                        System.exit(0);
                    }
                    String commitID = args[1];
                    String checkoutFN1 = args[3];
                    c.checkout2(commitID, checkoutFN1);
                } else if (args.length == 2) {
                    if (!c.saveInit()) {
                        System.out.println("Directory not initialized");
                        System.exit(0);
                    }
                    String branchName = args[1];
                    c.checkout3(branchName);
                } else {
                    System.out.println("Incorrect operands.");
                    System.exit(0);
                }
                break;
            case "rm":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
                if (args.length != 2) {
                    System.out.println("Please enter the "
                            + "right amount of arguments");
                    System.exit(0);
                }
                String fN = args[1];
                c.rm(fN);
                break;
            case "rm-branch":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
                if (args.length != 2) {
                    System.out.println("Please enter the right amount of arguments");
                    System.exit(0);
                }
                String branchName = args[1];
                c.rmBranch(branchName);
                break;
            case "log":
                if (args.length > 2) {
                    System.out.println("Please enter git --log only");
                    System.exit(0);
                }
                c.log();
                break;
            case "status":
                if (!c.saveInit()) {
                    System.out.println("Not an initialized Gitlet directory.");
                    System.exit(0);
                }
                c.status();
                break;
            case "global-log":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
                c.globalLog();
                break;
            case "find":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
                String findMessage = args[1];
                c.find(findMessage);
                break;
            case "reset":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
                String commitID = args[1];
                c.reset(commitID);
                break;
            case "branch":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
                if (args.length > 3) {
                    System.out.println("Please enter the "
                            + "right amount of arguments");
                    System.exit(0);
                }
                String branchNameB = args[1];
                c.branch(branchNameB);
                break;
            case "merge":
                if (!c.saveInit()) {
                    System.out.println("Directory not initialized");
                    System.exit(0);
                }
            default:
                System.out.println("No command with that name exists.");
        }
    }
}
