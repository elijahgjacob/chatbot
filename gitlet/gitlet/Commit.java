package gitlet;

import java.io.File;
import java.io.Serializable;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TreeMap;

public class Commit implements Serializable {
    /**
     * Current Working Directory.
     */
    static final File CWD = new File(".");

    /**
     * Main folder.
     */
    static final File GITLET_DIR = new File(CWD, ".gitlet");

    /**
     * Directory folder that contains each commit hash.
     */
    static final File COMMIT_DIR = Utils.join(GITLET_DIR, "commits");
    /**
     * Directory folder that contains each commit hash.
     */
    private final SimpleDateFormat timeFormat =
            new SimpleDateFormat("EEE MMM d HH:mm:ss YYYY Z");
    /**
     * TreeMap for storing fileNames and their according BlobIDs.
     **/
    private final String message;
    /**
     * TreeMap for storing fileNames and their according BlobIDs.
     **/
    private final String timestamp;
    /**
     * TreeMap for storing fileNames and their according BlobIDs.
     **/
    private final String parentID1;
    /**
     * TreeMap for storing fileNames and their according BlobIDs.
     **/
    private final String commitID;

    /**
     * TreeMap for storing fileNames and their according BlobIDs
     **/
    private final TreeMap<String, String> fileNameToBlobID;

    public Commit(String message, TreeMap<String, String> fileNameToBlobID, String parentID1) {
        this.parentID1 = parentID1;
        this.message = message;
        Date date = new Date();
        timestamp = timeFormat.format(date);
        this.commitID = hash();
        this.fileNameToBlobID = fileNameToBlobID;
    }

    /**
     * TreeMap for storing fileNames and their according
     * BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @param commitID
     * @returns map
     **/
    public static Commit readCommit(String commitID) {
        Commit c;
        File inFile = Utils.join(".gitlet/commits/", commitID);
        c = Utils.readObject(inFile, Commit.class);
        return c;
    }

    /**
     * TreeMap for storing fileNames and their according
     * BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @param commit
     **/
    public static void saveCommit(Commit commit) {
        File inFile = Utils.join(COMMIT_DIR, commit.getCommitID());
        Utils.writeObject(inFile, commit);
    }

    /**
     * TreeMap for storing fileNames and their
     * according BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @returns map
     **/
    public TreeMap<String, String> fileNameToBlobID() {
        return this.fileNameToBlobID;
    }

    /**
     * Method adds the commit by commitID to the branchName
     *
     * @param fileName
     * @return fileName
     **/
    public String getFileNameToBlobID(String fileName) {
        return this.fileNameToBlobID.get(fileName);
    }

    /**
     * Method adds the commit by commitID
     * to the branchName
     *
     * @param fileName
     * @param blobID
     **/
    public void updateFileNameToBlobID(String fileName, String blobID) {
        fileNameToBlobID.put(fileName, blobID);
    }

    /**
     * TreeMap for storing fileNames and their
     * according BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @returns map
     **/
    public String getCommitID() {
        return this.commitID;
    }

    /**
     * TreeMap for storing fileNames and their
     * according BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @returns map
     **/
    public String getMessage() {
        return this.message;
    }

    /**
     * TreeMap for storing fileNames and their
     * according BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @returns map
     **/
    public String getTime() {
        return this.timestamp;
    }

    /**
     * TreeMap for storing fileNames and their
     * according BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @returns map
     **/
    public String getParentID1() {
        return this.parentID1;
    }

    /**
     * TreeMap for storing fileNames and their
     * according BlobIDs //fileName, BlobID //wug.txt, BlobID.
     *
     * @returns map
     **/
    public String hash() {
        String hash = Utils.sha1(Utils.serialize(this));
        return hash;
    }

}
