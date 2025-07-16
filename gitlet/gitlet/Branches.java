package gitlet;

import java.io.*;
import java.util.TreeMap;


public class Branches implements Serializable {
    /**
     * <String, String> <branchname, commitID>.
     **/
    private final TreeMap<String, String> branchNameToCommit;

    /**
     * Branch constructor.
     **/
    public Branches() {
        this.branchNameToCommit = new TreeMap<>();
    }

    /**
     * Returns the Branch object with that branchName.
     *
     * @return blkn
     * @oaram branches
     */
    public static Branches readBranches(String branches) {
        Branches b;
        File inFile = new File(".gitlet/" + branches);
        try {
            ObjectInputStream inp =
                    new ObjectInputStream(new FileInputStream(inFile));
            b = (Branches) inp.readObject();
            inp.close();
        } catch (IOException | ClassNotFoundException excp) {
            b = null;
        }
        return b;
    }

    public static void saveBranch(Branches b) {
        Utils.writeObject(Commands.BRANCHES, b);
    }

    /**
     * Method returns branchName to Commit TreeMap.
     **/
    public TreeMap<String, String> getBranchNameToCommit() {
        return this.branchNameToCommit;
    }

    /**
     * Method gets the commit ID of the latest commit on that branch.
     *
     * @param branchName
     * @return xyz
     **/
    public String getCommitIDForBranch(String branchName) {
        return this.branchNameToCommit.get(branchName);
    }

    /**
     * Method adds the commit by commitID to the branchName.
     * @param commitID
     **/

    /**
     * Method adds the commit by commitID to the branchName.
     *
     * @param branchName
     * @param commitID
     **/
    public void updateBranch(String branchName, String commitID) {
        branchNameToCommit.put(branchName, commitID);
    }

    /**
     * Method removes the branch by branchName.
     *
     * @param branchName
     **/
    public void removeBranch(String branchName) {
        branchNameToCommit.remove(branchName);
    }
}
