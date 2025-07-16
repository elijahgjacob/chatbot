package enigma;

import org.junit.Test;
import org.junit.Rule;
import org.junit.rules.Timeout;
import static org.junit.Assert.*;

import static enigma.TestUtils.*;

/** The suite of all JUnit tests for the Permutation class.
 *  @author Elijah G. Jacob
 */
public class PermutationTest {

    /**
     * Testing time limit.
     */
    @Rule
    public Timeout globalTimeout = Timeout.seconds(5);

    /* ***** TESTING UTILITIES ***** */

    private Permutation perm;
    private String alpha = UPPER_STRING;

/**
 * Check that perm has an alphabet whose size is that of
 * FROMALPHA and TOAiiLPHA and that maps each character of
 * FROMALPHA to the corresponding character of FROMALPHA, and
 * vice-versa. TESTID is used in error messages.
 */
    private void checkPerm(String testId,
                           String fromAlpha, String toAlpha) {
        int N = fromAlpha.length();
        assertEquals(testId + " (wrong length)", N, perm.size());
        for (int i = 0; i < N; i += 1) {
            char c = fromAlpha.charAt(i), e = toAlpha.charAt(i);
            assertEquals(msg(testId, "wrong translation of '%c'", c),
                    e, perm.permute(c));
            assertEquals(msg(testId, "wrong inverse of '%c'", e),
                    c, perm.invert(e));
            int ci = alpha.indexOf(c), ei = alpha.indexOf(e);
            assertEquals(msg(testId, "wrong translation of %d", ci),
                    ei, perm.permute(ci));
            assertEquals(msg(testId, "wrong inverse of %d", ei),
                    ci, perm.invert(ei));
        }
    }

    @Test
    public void checkIdTransform() {
        perm = new Permutation("", UPPER);
        checkPerm("identity", UPPER_STRING, UPPER_STRING);
    }

    @Test
    public void checkSimplepermutation() {
        perm = new Permutation("(ABCD)", new Alphabet("ABCD"));
        checkPerm("simple", "ABCD", "BCDA");
    }
    @Test
    public void checkSimplepermutation1() {
        perm = new Permutation("(AB)(CD)(EFG)", new Alphabet("ABCDEFG"));
        assertEquals('B', perm.permute('A'));
        assertEquals('A', perm.permute('B'));
        assertEquals('E', perm.permute('G'));
    }


    @Test
    public void checkcomplexpermutation() {
        perm = new Permutation("(XZL)(BE)(KAQP)", new Alphabet("XZLBEKAQPG"));
        assertEquals('Z', perm.permute('X'));
        assertEquals('B', perm.permute('E'));
        assertEquals('Q', perm.permute('A'));
    }

    @Test
    public void checkedgepermutation() {
        perm = new Permutation("(L)(D)(Q)", new Alphabet("LDQ"));
        assertEquals('L', perm.permute('L'));
        assertEquals('D', perm.permute('D'));
        assertEquals('Q', perm.permute('Q'));
        assertFalse(perm.derangement());
    }

    @Test
    public void checkSimpleTransform() {
        perm = new Permutation("(BZT)(SH)(UAM)(JPLWQ)(EFN)", UPPER);
        String translated = "MZCDFNGSIPKWUEOLJRHBAVQXYT";
        checkPerm("simple", UPPER_STRING, translated);
    }

}
