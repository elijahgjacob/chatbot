package gitlet;

import java.io.File;
import java.io.Serializable;

public class Blobs implements Serializable {
    /**
     * Name of file.
     **/
    private final String name;
    /**
     * Hash of file.
     **/
    private final String blobID;
    /**
     * Contents as a byte array.
     **/
    private byte[] contents;
    /**
     * Contents as a string.
     **/
    private final String contentstr;
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
    static final File BLOBS_DIR = Utils.join(GITLET_DIR, "blobs");

    /**
     * Blob constructor inputs NAME.
     *
     * @param fileName
     **/
    public Blobs(String fileName) {
        File f = new File(fileName);
        this.name = fileName;
        this.contents = Utils.readContents(f);
        this.contentstr = Utils.readContentsAsString(f);
        this.blobID = hash();
    }

    public String getBlobID() {
        return this.blobID;
    }

    public String getcontentsstr() {
        return this.contentstr;
    }

    public void setContents(byte[] byteArray) {
        this.contents = byteArray;
    }

    /**
     * Returns hash generated.
     **/
    public String hash() {
        String hash = Utils.sha1(Utils.serialize(contents));
        return hash;
    }

    public static Blobs getBlob(String blobID) {
        Blobs b;
        File inFile = Utils.join(".gitlet/blobs/", blobID);
        b = Utils.readObject(inFile, Blobs.class);
        return b;
    }

    public static void saveBlob(Blobs b) {
        File inFile = new File(BLOBS_DIR, b.getBlobID());
        Utils.writeObject(inFile, b);
    }
}
