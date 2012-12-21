whamnospellgood
===============

Python script that totals up all the spelling mistakes in the top stories on 13wham.com ...

Connects to http://m.13wham.com/display/1438 (at the time of thie script being authored this was the "top stories" page) and pulls down the links to the top stories.

It then pulls the story text out of the <p> within the <div class="StoryBlock">.

It uses nltk to then tokenize everything.  Removes all tokens that are 1, 2, or 3 'chars' in length.  Spell checks words that only have letters in them using enchant.

The reason for writing this is because the wife and I always noticed the high number of spelling errors within the stories ... I wanted a hard number.


