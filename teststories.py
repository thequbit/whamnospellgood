from bs4 import BeautifulSoup
import urllib
import urllib2
import sys
import re
import types
import nltk
import enchant
import string



def is_spelled_correctly(word):

	correct = True

	if re.match("^[A-Za-z]*$", word):
		d = enchant.Dict("en_US")
		correct = d.check(word)
		#rint "Word = " + word + ", correct = " + correct.__str__()
	
	return correct 

def main(argv):

	#print is_spelled_wrong("asgasgesG")

	# define our 'top stories' url
	topstoriesurl = "http://m.13wham.com/display/1438"
	baseurl = "http://m.13wham.com"

	print "Getting top story page from m.13wham.com ..."
	html = urllib2.urlopen(topstoriesurl)
	print "... done"

	print "Getting links from top story page ..."
	soup = BeautifulSoup(html,from_encoding="utf-8")
	atags = soup.find_all('a', href=True)
	print "... done"

	totalmistakes = 0

	print "Pulling text from each story ..."
	# crate our patern to only pull links that have "story" in the path
	#repatern = re.compile("story*")
	for tag in atags:
		
		#print "Processing: " + tag['href']
		# if it's actually a story link
		if tag['href'].find("story") != -1:

			# generate the url so it is complete for the urllib2 engine
			storyurl = baseurl + tag['href']

			print "Processing Story: " + storyurl

			# check the db to see if we have already processed the story
			#print "     Checking database for story ..."
			#check_db_for_story(storyurl)
			

			# pull down the links contents
			storyhtml = urllib2.urlopen(storyurl)

			# run beautiful soup on the story html
			storysoup = BeautifulSoup(storyhtml,from_encoding="utf-8")

			# pull the text from the StoryBlock div tag
			storytag = storysoup.find("div",attrs={"class": "StoryBlock"})
			storytext = nltk.clean_html(storytag.__str__())
			
			# tokenize the story
			tokens = nltk.word_tokenize(storytext)
			words = nltk.FreqDist(word.lower() for word in tokens)

			#print type(words)

			# remove all length 1, 2, and 3 words
			for word in words:
				if len(word) < 4:
					del words[word]
#				else:
#					if re.match("^[A-Za-z]*$", word):

			# set our vounter (back) to zero
			mistakes = 0

			#print type(words)

			print "     Spell checking " + len(words.items()).__str__() + " words ..."

			for word in words:
				if is_spelled_correctly(word) == False:
					mistakes += 1

			print "     Story had spelling " + mistakes.__str__() + " errors in it."
			print ""

			totalmistakes += mistakes

	print "... done"

	print "Today's Top storries had " + totalmistakes.__str__() + " spelling mistakes in them."

if __name__ == '__main__': sys.exit(main(sys.argv))

