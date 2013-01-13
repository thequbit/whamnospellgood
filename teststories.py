from bs4 import BeautifulSoup
import urllib
import urllib2
import sys
import re
import types
import nltk
import enchant
import string
import datetime
import _mysql as mysql

def get_mysql_credentials():
	# read in credentials file
	lines = tuple(open('mysqlcreds.txt', 'r'))
	
	# return the tuple of the lines in the file
	# 
	# host
	# dbname
	# username
	# password
	#
	return lines

def spell_check_with_google(word):
	gurl = "https://www.google.com/search?q=" + word

	#print "Asking Google: " + gurl

	#send the word to google
	hdrs = { 'User-Agent': "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11" }
	urlreq = urllib2.Request(gurl,headers=hdrs)
	ghtml = urllib2.urlopen(urlreq)
	gsoup = BeautifulSoup(ghtml)

	#get all <p> with class="sp_cnt"
	spcnt = gsoup.find("p",attrs={"class": "sp_cnt"})
	spellng = gsoup.find("span",attrs={"class": "spell ng"})

	#see if we got anything returned
	if spcnt.__str__() == "None" and spellng.__str__() == "None":
		return True
	else:
		return False

def push_results_to_db(results,totalmistakes):
	
	# get our db info from our local file
	dbcreds = get_mysql_credentials()

	# decode responce
	host = dbcreds[0].rstrip()
	dbname = dbcreds[1].rstrip()
	username = dbcreds[2].rstrip()
	password = dbcreds[3].rstrip()

	# connect to our database
	database = mysql.connect(host=host,user=username,passwd=password,db=dbname)

	currenttime = datetime.datetime.now()

	print "\tPushing " + len(results).__str__()  + " results to database ..."   

	# push each result to the database
	for result in results:
		# put the result into the database
		query = 'insert into results (storyurl,mistakes,wordcount,resultdatetime) values("' + result[0] + '", ' + result[1].__str__() + ', ' + result[2].__str__() + ', "' + currenttime.strftime("%Y-%m-%d %H:%M") + '")'
		database.query(query)

	# put the run into the database
	query = 'insert into runs (rundatetime,totalmistakes) values("' + currenttime.strftime("%Y-%m-%d %H:%M") + '", ' + totalmistakes.__str__() + ')'
	database.query(query)
		
	print "\t... done"


def is_spelled_correctly(word):

	correct = True

	if re.match("^[A-Za-z]*$", word):
		d = enchant.Dict("en_US")
		correct = d.check(word)
		#rint "Word = " + word + ", correct = " + correct.__str__()
		
		# if the word is spelled incorrectly, use google to check to see if it isn't
		# a proper noun.
		if( correct == False ):
			print '\tWord misspelled, checking "{0}" against Google ...'.format(word)

			if spell_check_with_google(word) == False:
				print "\t\tNot spelled correctly."
			else:
				print "\t\tWord spelled correctly, perhaps proper noun."
				
				# set correct to True, since google said it was spelled correctly ...
				correct = True

			print "\t... done"

	
	return correct 

def main(argv):

	print "Start Of Script"

	#results = []
	#results.append(("google.com",1))
	#results.append(("yahoo.com",2))
	#push_results_to_db(results,4)

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

	# keep track of our total number of mistakes to report as output text
	totalmistakes = 0

	# create an array to put our results into
	results = []

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

			# pull down the links contents
			storyhtml = urllib2.urlopen(storyurl)

			# run beautiful soup on the story html
			storysoup = BeautifulSoup(storyhtml,from_encoding="utf-8")

			# pull the text from the StoryBlock div tag
			storytag = storysoup.find("div",attrs={"class": "StoryBlock"})
			storytext = nltk.clean_html(storytag.__str__())
			
			# tokenize the story
			tokens = nltk.word_tokenize(storytext)
			words = nltk.FreqDist(word for word in tokens)

			# remove all length 1, 2, and 3 words
			for word in words:
				if len(word) < 4:
					del words[word]

			# set our vounter (back) to zero
			mistakes = 0

			print "\tSpell checking " + len(words).__str__() + " words."

			# iterate through the words and spell check them
			for word in words:
				if is_spelled_correctly(word) == False:
					mistakes += 1

			print "\tStory had spelling " + mistakes.__str__() + " errors in it."
			print ""

			# create a tuple with the url and the mistake count
			result = (storyurl,mistakes,len(words))


			# add the result to the list of results
			results.append(result)

			# increment our total mistakes count for reporting
			totalmistakes += mistakes

	print "... done"

	print "Top storries had " + totalmistakes.__str__() + " spelling mistakes in them."

	# push the results for this run to the database
	push_results_to_db(results,totalmistakes)

	print "End Of Script."

if __name__ == '__main__': sys.exit(main(sys.argv))

