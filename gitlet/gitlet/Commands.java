package gitlet;

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.TreeMap;
import java.util.TreeSet;

import static gitlet.Utils.*;

public class Commands implements Serializable {
    /**
     * Current Working Directory.
     */
    static final File CWD = new File(System.getProperty("user.dir"));
    /**
     * Main metadata folder.
     */
    static final File GITLET_DIR = Utils.join(CWD, ".gitlet");
    /**
     * Directory folder that every commit.
     */
    static final File COMMIT_DIR = Utils.join(GITLET_DIR, "commits");
    /**
     * Directory folder that holds every blob.
     */
    static final File BLOBS_DIR = Utils.join(GITLET_DIR, "blobs");
    /**
     * File that holds the Head commitID.
     */
    static final File HEAD = Utils.join(GITLET_DIR, "HEAD");
    /**
     * File that holds the StagingArea object.
     */
    static final File STAGING_AREA = Utils.join(GITLET_DIR, "STAGING_AREA");
    /**
     * File that holds the Branches object.
     */
    static final File BRANCHES = Utils.join(GITLET_DIR, "BRANCHES");
    /**
     * File that holds the message.
     */
    private static String message = "";
    /**
     * File that holds the Head commitID.
     */
    private final String parentID1 = " ";
    /**
     * File that holds the timestampe.
     */
    private final String timestamp = " ";
    /**
     * File that holds the Head commitID.
     */
    private final String stagingAreaFn = "STAGING_AREA";
    /**
     * File that holds the Head commitID.
     */
    private final String headFn = "HEAD";
    /**
     * File that holds the Head commitID.
     */
    private final String branchesFn = "BRANCHES";

    /**
     * Method for init command.
     */
    public void init() throws IOException, ClassNotFoundException {
        new File(".gitlet").mkdir();
        new File(".gitlet/commits").mkdir();
        new File(".gitlet/merge").mkdir();
        new File(".gitlet/blobs").mkdir();
        join(".gitlet", headFn);
        join(".gitlet", branchesFn);
        join(".gitlet", stagingAreaFn);
        StagingArea stage = new StagingArea();
        StagingArea.updateStage(stage.toAdd, stage.toRemove);
        StagingArea.saveStagingArea(stage);
        TreeMap<String, String> fileNametoBlobID = new TreeMap<>();
        message = "initial commit";
        Commit initialCommit = new Commit(message, fileNametoBlobID, null);
        String initialCommitID = initialCommit.getCommitID();
        Commit.saveCommit(initialCommit);
        Branches b = new Branches();
        b.updateBranch("master", initialCommitID);
        Branches.saveBranch(b);
        Head h = new Head();
        h.updateHead(initialCommitID, "master");
        Head.saveHead(h);
    }

    /**
     * Method to check if directory exists.
     *
     * @return t/f
     */
    public boolean saveInit() {
        return GITLET_DIR.exists();
    }

    /**
     * Add method.
     *
     * @param fN
     * @return t/f
     */
    public boolean add(String fN) throws NullPointerException {
        StagingArea stage = StagingArea.readStagingArea(stagingAreaFn);
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Commit headCommit = Commit.readCommit(headCommitID);
        File file = new File(fN);
        if (!file.exists()) {
            return false;
        }
        if (stage == null) {
            System.out.println("Stage doesn't exist.");
            System.exit(0);
        }
        try {
            if (stage.toAdd.containsKey(fN)) {
                System.out.println("Nothing to add.");
                return false;
            }
            if (stage.toRemove.containsKey(fN)) {
                stage.toRemove.remove(fN);
                StagingArea.updateStage(stage.toAdd, stage.toRemove);
                StagingArea.saveStagingArea(stage);
                return true;
            }
            if (headCommit.fileNameToBlobID().containsKey(fN)) {
                String s = headCommit.getFileNameToBlobID(fN);
                Blobs b = new Blobs(fN);
                if (s.equals(b.getBlobID())) {
                    System.exit(0);
                }
            }
            Blobs bl = new Blobs(fN);
            stage.toAdd.put(fN, bl.getBlobID());
            Blobs.saveBlob(bl);
            StagingArea.updateStage(stage.toAdd, stage.toRemove);
            StagingArea.saveStagingArea(stage);
            return true;
        } catch (NullPointerException excp) {
            System.out.println("Stage is empty");
            return false;
        }
    }

    /**
     * rm method.
     *
     * @param fN
     */
    public void rm(String fN) throws NullPointerException {
        StagingArea stage = StagingArea.readStagingArea(stagingAreaFn);
        File f = Utils.join(CWD, fN);
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Commit headCommit = Commit.readCommit(headCommitID);
        if (stage.toAdd.size() != 0) {
            if (stage.toAdd.containsKey(fN)) {
                stage.toAdd.remove(fN);
                StagingArea.updateStage(stage.toAdd, stage.toRemove);
                StagingArea.saveStagingArea(stage);
                System.exit(0);
            }
        } else if (headCommit.fileNameToBlobID().containsKey(fN)) {
            String blobId = headCommit.fileNameToBlobID().get(fN);
            stage.toRemove.put(fN, blobId);
            StagingArea.updateStage(stage.toAdd, stage.toRemove);
            StagingArea.saveStagingArea(stage);
            Utils.restrictedDelete(f);
            System.exit(0);
        } else {
            System.out.println("No reason to remove the file.");
        }

    }

    /**
     * commit method.
     *
     * @param message
     */
    public void commit(String message) {
        StagingArea stage = StagingArea.readStagingArea(stagingAreaFn);
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Commit headCommit = Commit.readCommit(headCommitID);
        TreeMap<String, String> updatedContents = new TreeMap<>();
        if (stage.toAdd.isEmpty()) {
            if (stage.toRemove.isEmpty()) {
                System.out.println("No changes added to the commit.");
                System.exit(0);
            }
        }
        if (headCommit.fileNameToBlobID().isEmpty()) {
            for (String filename : stage.toAdd.keySet()) {
                String blobID = stage.toAdd.get(filename);
                updatedContents.put(filename, blobID);
                Blobs bl = new Blobs(filename);
                Blobs.saveBlob(bl);
            }
        } else {
            for (String filename : headCommit.fileNameToBlobID().keySet()) {
                String blobID = headCommit.getFileNameToBlobID(filename);
                updatedContents.put(filename, blobID);
                Blobs bl = Blobs.getBlob(blobID);
                Blobs.saveBlob(bl);
            }
            for (String filename : stage.toAdd.keySet()) {
                String blobID = stage.toAdd.get(filename);
                updatedContents.put(filename, blobID);
                Blobs bl = Blobs.getBlob(blobID);
                Blobs.saveBlob(bl);

            }
            for (String filename : stage.toRemove.keySet()) {
                String blobID = stage.toRemove.get(filename);
                updatedContents.remove(filename, blobID);
                Blobs bl = Blobs.getBlob(blobID);
                Blobs.saveBlob(bl);

            }
        }
        Commit next = new Commit(message, updatedContents, headCommitID);
        String newCommitID = next.getCommitID();
        Branches b = Branches.readBranches(branchesFn);
        String branchName = h.getBranchName();
        b.updateBranch(branchName, newCommitID);
        h.updateHead(newCommitID, branchName);
        Head.saveHead(h);
        Commit.saveCommit(next);
        Branches.saveBranch(b);
        stage.toAdd.clear();
        stage.toRemove.clear();
        StagingArea.saveStagingArea(stage);
    }

    /**
     * checkout method.
     *
     * @param fileName
     * @return t/f
     */
    public boolean checkout1(String fileName) {
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Commit headCommit = Commit.readCommit(headCommitID);
        if (headCommit.fileNameToBlobID().containsKey(fileName)) {
            String blobID = headCommit.getFileNameToBlobID(fileName);
            Blobs b = Blobs.getBlob(blobID);
            Blobs.saveBlob(b);
            writeContents(join(CWD, fileName), b.getcontentsstr());
            return true;
        }
        System.out.println("File does not exist in that commit");
        return false;
    }

    /**
     * Method to checkout.
     *
     * @param fN
     * @param commitID
     */
    public void checkout2(String commitID, String fN) {
        List<String> commitsList = plainFilenamesIn(COMMIT_DIR);
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Commit headCommit = Commit.readCommit(headCommitID);
        if (!commitsList.contains(commitID)) {
            System.out.println("No commit with that id exists.");
            System.exit(0);
        }
        Commit c = Commit.readCommit(commitID);
        if (!c.fileNameToBlobID().containsKey(fN)) {
            System.out.println("File does not exist in that commit.");
            System.exit(0);
        } else {
            for (String headFName : headCommit.fileNameToBlobID().keySet()) {
                if (headCommit.fileNameToBlobID().containsKey(headFName)) {
                    join(CWD, headFName).delete();
                }
                String blobID = c.getFileNameToBlobID(fN);
                Blobs b = Blobs.getBlob(blobID);
                writeContents(join(CWD, fN), b.getcontentsstr());
            }

        }
    }

    /**
     * Method to checkout.
     *
     * @param branchName
     */
    public void checkout3(String branchName) {
        boolean untrackedFileIsPresent = false;
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Commit headCommit = Commit.readCommit(headCommitID);
        Branches branches = Branches.readBranches(branchesFn);
        if (branches.getCommitIDForBranch(branchName) == null) {
            System.out.println("No such branch exists.");
            System.exit(0);
        }
        if (h.getBranchName().equals(branchName)) {
            System.out.println("No need to checkout the current branch.");
            System.exit(0);
        }
        String branchHeadCommitID =
                branches.getBranchNameToCommit().get(branchName);
        Commit branchHeadCommit =
                Commit.readCommit(branchHeadCommitID);
        for (String filename :
                branchHeadCommit.fileNameToBlobID().keySet()) {
            File f = new File(filename);
            if (!headCommit.fileNameToBlobID().containsKey(filename)
                    && f.exists()) {
                untrackedFileIsPresent = true;
                break;
            }
        }
        if (untrackedFileIsPresent) {
            System.out.println("There is an untracked file "
                    + "in the way; delete it, or add and commit it first.");
            System.exit(0);
        }
        for (String fN : headCommit.fileNameToBlobID().keySet()) {
            if (!branchHeadCommit.fileNameToBlobID().containsKey(fN)) {
                join(CWD, fN).delete();
            }
        }
        for (String fN : branchHeadCommit.fileNameToBlobID().keySet()) {
            String blobID = branchHeadCommit.fileNameToBlobID().get(fN);
            Blobs b = Blobs.getBlob(blobID);
            writeContents(join(CWD, fN), b.getcontentsstr());
            Blobs.saveBlob(b);
        }
        h.updateHead(branchHeadCommitID, branchName);
        branches.updateBranch(branchName, branchHeadCommitID);
        Head.saveHead(h);
        System.exit(0);
    }

    /**
     * Method to check the log.
     */
    public void log() {
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Commit headCommit = Commit.readCommit(headCommitID);
        try {
            while (headCommit != null) {
                System.out.println("===");
                System.out.println("commit " + headCommitID);
                System.out.println("Date: " + headCommit.getTime());
                System.out.println(headCommit.getMessage());
                System.out.println();
                headCommitID = headCommit.getParentID1();
                headCommit = Commit.readCommit(headCommitID);
            }
        } catch (NullPointerException excp) {
            System.exit(0);
        }
    }

    /**
     * Method for globalLog.
     */
    public void globalLog() {
        List<String> commitsList = plainFilenamesIn(COMMIT_DIR);
        for (String s : commitsList) {
            Commit c = Commit.readCommit(s);
            System.out.println("===");
            System.out.println("commit " + s);
            System.out.println("Date: " + c.getTime());
            System.out.println(c.getMessage());
            System.out.println();
        }
    }

    /**
     * find method.
     *
     * @param message
     */
    public void find(String message) {
        List<String> commitsList = plainFilenamesIn(COMMIT_DIR);
        boolean exists = false;
        for (String s : commitsList) {
            if (Commit.readCommit(s).getMessage().equals(message)) {
                System.out.println(s);
                exists = true;
            }
        }
        if (!exists) {
            System.out.println("Found no commit with that message.");
        }
    }

    public void reset(String commitID) {
        List<String> commitsList = plainFilenamesIn(COMMIT_DIR);
        boolean exists = false;
        for (String f : commitsList) {
            if (f.equals(commitID)) {
                exists = true;
                break;
            }
        }
        if (!exists) {
            System.out.println("No commit with that id exists.");
            System.exit(0);
        }
        Commit c = Commit.readCommit(commitID);
        Head h = Head.readHead(headFn);
        Commit headCommit = Commit.readCommit(h.getCommitID());
        String currBranchName = h.getBranchName();
        Branches branches = Branches.readBranches(branchesFn);
        StagingArea stage = StagingArea.readStagingArea(stagingAreaFn);
        for (String fN : c.fileNameToBlobID().keySet()) {
            File f = new File(fN);
            if (!headCommit.fileNameToBlobID().
                    containsKey(fN) && f.exists()) {
                System.out.println("There is an untracked file in the way; "
                        + "delete it, or add and commit it first.");
                Utils.join(CWD, fN).delete();
            } else {
                String blobID = c.getFileNameToBlobID(fN);
                Blobs b = Blobs.getBlob(blobID);
                h.updateHead(commitID, currBranchName);
                branches.updateBranch(currBranchName, commitID);
                writeContents(join(CWD, fN), b.getcontentsstr());
            }
        }
        if (exists) {
            stage.toAdd.clear();
            stage.toRemove.clear();
            StagingArea.saveStagingArea(stage);
            Branches.saveBranch(branches);
        } else {
            System.out.println("Found no commit with that message.");
        }
    }

    /**
     * branch method.
     *
     * @param branchNameB
     */
    public void branch(String branchNameB) {
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        Branches b = Branches.readBranches(branchesFn);
        if (b.getCommitIDForBranch(branchNameB) != null) {
            System.out.println("A branch with that name already exists.");
            System.exit(0);
        } else {
            b.updateBranch(branchNameB, headCommitID);
            Branches.saveBranch(b);
            System.exit(0);
        }
    }

    /**
     * rmBranch method.
     *
     * @param branchNameB
     */
    public void rmBranch(String branchNameB) {
        Head h = Head.readHead(headFn);
        Branches b = Branches.readBranches(branchesFn);
        if (b.getCommitIDForBranch(branchNameB) == null) {
            System.out.println("A branch with that name does not exist.");
            System.exit(0);
        } else if (h.getBranchName().equals(branchNameB)) {
            System.out.println("Cannot remove the current branch.");
            System.exit(0);
        } else {
            b.removeBranch(branchNameB);
            Branches.saveBranch(b);
            System.exit(0);
        }
    }

    /**
     * status method.
     */
    public void status() {
        StagingArea stage;
        stage = StagingArea.readStagingArea("STAGING_AREA");
        Branches b;
        b = Branches.readBranches(branchesFn);
        Head h = Head.readHead(headFn);
        String headCommitID = h.getCommitID();
        System.out.println("=== Branches ===");
        for (String s : b.getBranchNameToCommit().keySet()) {
            if (b.getCommitIDForBranch(s).equals(headCommitID)) {
                System.out.print("*");
            }
            System.out.println(s);
        }
        System.out.println();
        System.out.println("=== Staged Files ===");
        for (String s : stage.getToAdd().keySet()) {
            System.out.println(s);
        }
        System.out.println();
        System.out.println("=== Removed Files ===");
        for (String s : stage.getToRemove().keySet()) {
            System.out.println(s);
        }
        System.out.println();
        System.out.println("=== Modifications Not Staged For Commit ===");
        System.out.println();
        System.out.println("=== Untracked Files ===");
        System.out.println();
    }

    /**
     * ifAncestor method.
     *
     * @param branchHeadCommit
     * @param headCommit
     * @param splitPointID
     * @param h
     * @param branches
     * @param branchName
     * @returns t/f
     */
    public boolean ifAncestor(Commit branchHeadCommit,
                              Commit headCommit, String splitPointID,
                              Head h, Branches branches, String branchName) {
        return true;
    }

    /**
     * getSplitPoints method.
     *
     * @param branchHeadCommit
     * @param headCommit
     * @return ID
     */
    public String getSplitPointID(Commit branchHeadCommit, Commit headCommit) {
        return "";
    }

    /**
     * ifMergeConflicts method.
     *
     * @param branchHeadCommit
     * @param splitPointID
     * @param headCommit
     * @param h
     * @param branches
     * @param branchName
     * @return t/f
     */
    public boolean ifFastForward(Commit branchHeadCommit, Commit headCommit,
                                 String splitPointID, Head h,
                                 Branches branches, String branchName) {
        return true;
    }

    /**
     * ifMergeConflicts method.
     *
     * @param branchHeadCommit
     * @param splitPointCommit
     * @param headCommit
     * @param fileName
     * @return t/f
     */
    public boolean ifMergeConflicts(Commit branchHeadCommit,
                                    Commit splitPointCommit,
                                    Commit headCommit, String fileName) {
        return true;
    }

    /**
     * merge method.
     *
     * @param branchName
     */
    public void merge(String branchName) {
        Head h = Head.readHead(headFn);
        StagingArea stage =
                StagingArea.readStagingArea(stagingAreaFn);
        Branches branches =
                Branches.readBranches(branchesFn);
        String branchHeadCommitID = branches.
                getBranchNameToCommit().get(branchName);
        Commit branchHeadCommit = Commit.
                readCommit(branchHeadCommitID);
        Commit headCommit = Commit.
                readCommit(h.getCommitID());
        String splitPointID =
                getSplitPointID(branchHeadCommit, headCommit);
        Commit splitPointCommit =
                Commit.readCommit(splitPointID);
        Boolean isAncestor = ifAncestor
                (branchHeadCommit, headCommit,
                        splitPointID, h, branches, branchName);
        Boolean isFastForward = ifFastForward
                (branchHeadCommit, headCommit,
                        splitPointID, h, branches, branchName);
        boolean fileConflict = false;
        if (isAncestor) {
            System.out.println("Given branch "
                    + "is an ancestor of the current branch.");
        }
        if (isFastForward) {
            System.out.println("Current branch fast-forwarded.");
        }
        TreeSet<String> fileNameList = new TreeSet<>();
        for (String s : headCommit.fileNameToBlobID().keySet()) {
            fileNameList.add(s);
        }
        for (String s : branchHeadCommit.
                fileNameToBlobID().keySet()) {
            fileNameList.add(s);
        }
        for (String fileName : fileNameList) {
            String headCommitContID = headCommit.
                    getFileNameToBlobID(fileName);
            String branchHeadCommitContID = branchHeadCommit.
                    getFileNameToBlobID(fileName);
            String splitPointContID = splitPointCommit.
                    getFileNameToBlobID(fileName);
            if (headCommitContID.isEmpty()
                    && branchHeadCommitContID.isEmpty()) {
                continue;
            }
            if (!headCommitContID.isEmpty()
                    && splitPointContID.isEmpty()) {
                continue;
            }
            if (!branchHeadCommitContID.isEmpty()
                    && splitPointContID.isEmpty()) {
                checkout2(branchHeadCommitID, fileName);
                stage.toAdd.put(fileName, branchHeadCommitID);
                continue;
            }
            Blobs headCommitCont = Blobs.getBlob
                    (headCommitContID);
            Blobs splitPointCont = Blobs.getBlob
                    (splitPointContID);
            if (branchHeadCommitContID.isEmpty()
                    && !splitPointContID.isEmpty()) {
                if (headCommitCont.getcontentsstr().
                        equals(splitPointCont.getcontentsstr())) {
                    rm(fileName);
                    stage.toRemove.put(fileName,
                            branchHeadCommitID);
                    continue;
                }
            }
            if (!splitPointCont.getcontentsstr().isEmpty()) {
                if (Blobs.getBlob(headCommitContID).
                        getcontentsstr().
                        equals(splitPointCont.getcontentsstr())) {
                    if (headCommitCont.getcontentsstr().isEmpty()) {
                        continue;
                    }
                }
            }
            Blobs branchHeadCommitCont = Blobs.
                    getBlob(branchHeadCommitContID);
            if (!headCommitCont.getcontentsstr().
                    equals(splitPointCont.getcontentsstr()) &&
                    branchHeadCommitCont.getcontentsstr().
                            equals(splitPointCont.getcontentsstr())) {
                continue;
            }
            if (headCommitCont.getcontentsstr().equals(
                    branchHeadCommitCont.getcontentsstr())) {
                continue;
            }
            if (ifMergeConflicts(branchHeadCommit,
                    splitPointCommit, headCommit, fileName)) {
                byte[] newContents;
                if (headCommitContID.isEmpty()) {
                    newContents = ("<<<<<<< HEAD\n"
                            + "=======\n"
                            + branchHeadCommitCont.getcontentsstr()
                            + ">>>>>>>").getBytes(StandardCharsets.UTF_8);
                } else if (branchHeadCommitContID.isEmpty()) {
                    newContents = ("<<<<<<< HEAD\n"
                            + headCommitCont.getcontentsstr()
                            + "=======\n"
                            + ">>>>>>>").getBytes(StandardCharsets.UTF_8);
                } else {
                    newContents = ("<<<<<<< HEAD\n"
                            + headCommitCont.getcontentsstr()
                            + "=======\n"
                            + branchHeadCommitCont.getcontentsstr()
                            + ">>>>>>>").getBytes(StandardCharsets.UTF_8);
                }
                headCommitCont.setContents(newContents);
                stage.toAdd.put(fileName, headCommitContID);
                commit("Merged [given branch name] into [current branch name]");
            }
        }
    }
}
