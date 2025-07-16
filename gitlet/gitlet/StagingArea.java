package gitlet;

import java.io.*;
import java.util.TreeMap;


public class StagingArea implements Serializable {
    /**
     * StagingArea CONSTRUCTOR.
     **/
    public TreeMap<String, String> toAdd =
            new TreeMap<String, String>();
    /**
     * StagingArea CONSTRUCTOR.
     **/
    public TreeMap<String, String> toRemove =
            new TreeMap<String, String>();
    /**
     * StagingArea CONSTRUCTOR.
     **/
    public String stagingID = "STAGING_AREA";

    /**
     * StagingArea CONSTRUCTOR.
     **/
    public StagingArea() {
    }

    /**
     * Method adds the commit by commitID to the branchName.
     *
     * @param toAdd
     * @param toRemove
     **/
    public static void updateStage(TreeMap<String,
            String> toAdd, TreeMap<String, String> toRemove) {
        toAdd = new TreeMap<>();
        toRemove = new TreeMap<>();
    }

    /**
     * StagingArea CONSTRUCTOR.
     *
     * @param stagingID
     * @return stage
     **/
    public static StagingArea readStagingArea(String stagingID) {
        StagingArea stage;
        File inFile = new File(".gitlet/" + stagingID);
        try {
            ObjectInputStream inp =
                    new ObjectInputStream(new FileInputStream(inFile));
            stage = (StagingArea) inp.readObject();
            inp.close();
        } catch (IOException | ClassNotFoundException excp) {
            stage = null;
        }
        return stage;
    }

    /**
     * StagingArea CONSTRUCTOR
     *
     * @param stage
     **/
    public static void saveStagingArea(StagingArea stage) {
        Utils.writeObject(Commands.STAGING_AREA, stage);
    }

    /**
     * StagingArea CONSTRUCTOR.
     *
     * @returns toAdd
     **/
    public TreeMap<String, String> getToAdd() {
        return toAdd;
    }

    /**
     * StagingArea CONSTRUCTOR.
     *
     * @returns toRemove
     **/
    public TreeMap<String, String> getToRemove() {
        return toRemove;
    }
}

