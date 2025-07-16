package gitlet;

import java.io.File;
import java.io.Serializable;

public class Head implements Serializable {
    /** Var for commitID*/
    private String commitID;
    /** Var for commitID*/
    private String branchName;

    /**
     * Constructor front commit of that branch.
     **/
    public Head() {
        this.commitID = commitID;
        this.branchName = branchName;
    }

    /**
     * Constructor front commit of that branch.
     * @return commit
     **/
    public String getCommitID() {
        return this.commitID;
    }

    /**
     * Constructor front commit of that branch.
     * @return commit
     **/
    public String getBranchName() {
        return branchName;
    }

    /** Method updates the instances in the Head object.
     * @param newCommitID
     * @param newBranchName
     */
    public void updateHead(String newCommitID, String newBranchName) {
        this.commitID = newCommitID;
        this.branchName = newBranchName;
    }



    /** Method reads the Head object to the file.
     * @returns Head object*/
    public static Head readHead(String headFn) {
        Head head;
        File inFile = new File(".gitlet/" + headFn);
        head = Utils.readObject(inFile, Head.class);
        return head;
    }

    /** Method saves the Head object to the file.
     * @param head object */
    public static void saveHead(Head head) {
        Utils.writeObject(Commands.HEAD, head);
    }
}
