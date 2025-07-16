# Gitlet Design Document
author: Elijah Jacob

## 1. Classes and Data Structures

##Commands
Contains all the methods required to run the program
###init()
Creates the folder structure to hold staging
####Variables used:
* Current Branch info
* Commit ID
* Parent ID

System should start off with one commit with no details 
Creates a directory for the Gitlet folder 
Commit 0 is initialized without any link to a blob (or contents)
Master is the active branch 
### add()
Sends the file to staging, if it is already in the staging and it is re-added, the original contents overwritten.
Only takes in one file in at a time
If it is in the remove area, and it is added, it is removed from the remove area.

####Variables used: 
* filename
* toAdd (TreeMap)
* toRemove (TreeMap)

### commit()
A new commit is added, staging is cleared. 
Each commit can be identified with its SHA-1 hash ID
key = original file name, value = byte[]
Storing all the additions and deletions to the code and to the files.
Every commit is added to the live branch
- branch data is stored as additions/deletions to the files

Info is stored in the repo.

####Variables used:
* SHA1 Hash ID
* Blob reference keys
* commit Hash 
  * ParentID
* Message 
* Timestamp

### log()
Displays information about all of the commits. 
Commits are registered with the SHA-1 Hash key
####Variables used: 
* Current commit 
* Timestamp
* Message

### checkout()
Replaces the code in the working directory from the HEAD of the commits.
The head wil now point to the front of the list

####Variables used:
* Branch ID
* Commit ID

## Diff
A comparison of two sequences of strings.  After executing setSequences to initialize the data, methods allow computing longest common sequences and differences in the form of edits needed to convert one sequence to the next.

####Variables used:
* name/key
* hashCode/value
* contents
##Branches
Initializes a parent Branch with a set branchID. Adds files of the same branch together into a LinkedList format.
####Variables used:
* parentID
* branches (LL)
* commitID

###merge(branch name)

We want to take the contents at the head of the given branch into the current branch
We try to merge the changes in the given branch unless no changes have been made in the given branch.

How do we figure out the split point?
We can go forwards but not backwards
- return given branch is an ancestor of the current branch

Gitlet merge scenario 1
- Modified in GIVEN branch but not CURRENT branch ==> use version in GIVEN
- Files staged

Scenario 2
Modified in current branch and in GIVEN branch the same way ==> nothing changes

Scenario 3
Not in SPLIT POINT but present in Current branch ==> Nothing changes

Scenario 6
Unmodified in CURRENT branch but deleted in GIVEN branch ==> remove file

Merge conflicts: 
- Modified in GIVEN branch and in CURRENT branch in different ways
- Examples
  - Contents changed differently
  - Deleted in one and chnaged contents in another

<<<<<<<<< HEAD
Hello Everyone!
=====
Hello!
>>>>>>

## Commit 
The commit directory is created from the gitlet folder. We see the timestamp is imported.
To store commits we will use LinkedHashMaps as their orders of KV are preserved. This is important especially with commits to ensure that the order is kept.
This class is used to serialize and hash:
* The initial commit when init() is called
* When a file is committed
We should call the initialhash function when Commands.init() is called.
The commitHash combines the title, time stamp , message and contents and then SHA-1 Hash and Serialize the commit hash.
AFter this we try to apply some persistance with saveCommit().

A commit can have two parents which is what makes a commit tree
-For normal commits, parent2 is null

Tips:
See how to reuse old commands
Be dilligent about writing if statements to detect each of the 8 merge scanrio; clearly define variable names
Read all of the variables in one go:
head, give, split points

Finding the split point works by traversing back and finding the point where two files have the same hash.
Use a tree traversal algorithm to view commits in order of their distance to the current branch head
## DumpObj
A debugging class whose main program may be invoked as follows: java gitlet.DumpObj FILE...  where each FILE is a file produced by Utils.writeObject (or any file  containing a serialized object).  This will simply read FILE,
deserialize it, and call the dump method on the resulting Object.
## Main
Where the driver code is found and the input commands are registered. Validation is also included to great extent with arguments, switch and cases,
## UnitTest
Tests we would check for are for accuracy with:
1. Commits
2. Blobs
3. A test for every function 
## Utils 
This class contains all the functions required for file processing 
                                                  
##Branches                                            
Contains the code that initializes and sets branches with the LinkedList data structure 

##Staging Area                                                                                   
Contains the code that creates the staging area and separates what is staged for removal. Uses two HashMaps to see what files are staged for addition and what are staged for removal.
We create a file directory for this section for which we have two directories. One for addition and one for removal. Once a file is committed or removed using the git -commit, git -add commands, it is moved from here to the repository.

## 2. Algorithms

This is where you tell us how your code works. For each class, include
a high-level description of the methods in that class. That is, do not
include a line-by-line breakdown of your code, but something you would
write in a javadoc comment above a method, ***including any edge cases
you are accounting for***. We have read the project spec too, so make
sure you do not repeat or rephrase what is stated there.  This should
be a description of how your code accomplishes what is stated in the
spec.

The length of this section depends on the complexity of the task and
the complexity of your design. However, simple explanations are
preferred. Here are some formatting tips:

* For complex tasks, like determining merge conflicts, we recommend
  that you split the task into parts. Describe your algorithm for each
  part in a separate section. Start with the simplest component and
  build up your design, one piece at a time. For example, your
  algorithms section for Merge Conflicts could have sections for:

   * Checking if a merge is necessary.
   * Determining which files (if any) have a conflict.
   * Representing the conflict in the file.
  
* Try to clearly mark titles or names of classes with white space or
  some other symbols.

###add()
1. Checks if the file is a file to be removed by deserializing the files 
   1. If it is, remove it from the toRemove HashMap
2. Adds the filename to the hashmap of files to be staged
3. Checks if any of the commits have the commitID equal to the old files
   1. If it doesn't, 
      1. move the file contents to the commitmap by traversing through commitID
      2. add the blob to the blobs hashmap by traversing through blobID
      3. delete the file commitID from the StagingArea and the toAdd HashMap
   2. If they do delete the old file from staging

###init()
2. create the gitlet VCS
3. initialize the gitlet folder directory
4. create a directory for commits
5. setup persistence
6. create a new commit
7. Adds the Branch to Branches class.
8. If folder exists, prints out cannot initialize an existing repo.

###commit()
1. Apply the SHA-1 Hash on the Commit 0
2. Serialize the contents of the blob and turn it into byte[] format
3. Store the unique data it in a hashmap which then links to the branches class
4. Adds the serialized files to the commits 
5. The file name is added to the commits directory
6. The same are removed from the staging directory

###log()
1. Display current commit 
2. Displays previous commits in the LinkedList going back to the HEAD.

###checkout()                    
1. Puts all files from the HEAD into the CWD, whilst overwriting files 
2. Set the Head to the front of the commit links

## 3. Persistence

###Commit()
After running the commit function, I would need to ensure the state of my program remains the same across multiple runs. It would be hard to maintain the commit tree without keeping game state after a run.
We can do this by adding the file, and it's contents after every time the file is added.

We have setup a savefuntion as well to regularly save our files to the system.

## 4. Design Diagram

Attach a picture of your design diagram illustrating the structure of your
classes and data structures. The design diagram should make it easy to

![Image](/Users/elijahjacob/Downloads/IMG_7922.png)


