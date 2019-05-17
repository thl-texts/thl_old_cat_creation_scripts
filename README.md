# Dege Text Scripts

A series of scripts used to process the Degé Kangyur input texts. The texts were initially created from direct input. 
Then a second run of direct input was done by Esukhia while proofing the existing texts. These created proofed 
versions of each volume in the Kangyur only.

The original set os scripts in the folder "vs1scripts" were written by Than Grove bet. 2016-2018 to create new 
versions of each text using this proofed input. However, these new versions of texts themselves needed proofing. 
The texts were rebuilt based on the cataloging data. If the pagination was incorrect in the bibl record, then the 
wrong span of text would be used to create the proofed version. Furthermore, in at least one instance a page number 
was skipped in the Tibetan pagination on the volume margins. Whereas the Esukhia inputers kept numbering the pages 
according to their actual sequential number, the first inputers used the Tibetan number written in the margin of the pages. 
Thus, there was a one-page differential between the first and later inputs for about half that volume.

In May of 2018, Than began to refactor and document this code to 

1. make it easier to reconvert individual texts or 
a range of texts, 
2. be able to account for such pagination differentials in a volume, 
3. clean up the code to more 
properly utilize classes, inheritence and so forth, and 
4. to upgrade the code from Python 2 to Python 3, which for one
thing has better Unicode handling. 

To fascilitate the rewrite, Than moved all the original scripts into the 
"vs1scripts" (version 1 scripts) folder.