package gitlet;

import ucb.junit.textui;
import org.junit.Test;

import java.io.File;
import java.io.IOException;
import java.util.TreeMap;

import static org.junit.Assert.*;

/** The suite of all JUnit tests for the gitlet package.
 *  @author Elijah G. Jacob
 */
public class UnitTest {

    /** Run the JUnit tests in the loa package. Add xxxTest.class entries to
     *  the arguments of runClasses to run other JUnit tests. */
    public static void main(String[] ignored) {
        System.exit(textui.runClasses(UnitTest.class));
    }

    /** A dummy test to avoid complaint. */
    @Test
    public void initTest() {
        String message1 = "init";
        TreeMap<String, String> commitmap1 = new TreeMap<>();
        String message2 = "init";
        TreeMap<String, String> commitmap2 = new TreeMap<>();
        Commit commit1 = new Commit(message1, commitmap1, null);
        Commit commit2 = new Commit(message2, commitmap2,
                commit1.getCommitID());
        assertEquals(commit1.getCommitID(), commit2.getParentID1());
        assertNotEquals(commit1, commit2);
    }

    @Test
    public void initTest2() {
        String message2 = "init";
        TreeMap<String, String> commitmap2 = new TreeMap<>();
        String message3 = "init";
        TreeMap<String, String> commitmap3 = new TreeMap<>();
        Commit commit2 = new Commit(message2, commitmap2, null);
        Commit commit3 = new Commit(message3, commitmap3,
                commit2.getCommitID());
        assertEquals(commit2.getCommitID(), commit3.getParentID1());
        assertNotEquals(commit2, commit3);
    }

}


