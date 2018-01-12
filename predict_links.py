
import sqlite3
import ssl
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import requests
import re


filename = 'nfl_predictions.sqlite'
conn = sqlite3.connect(filename)
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Predictions;

CREATE TABLE Predictions (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
week INTEGER,
pundit TEXT,
team1 TEXT,
team2 TEXT,
score1 INTEGER,
score2 INTEGER,
just TEXT
)'''
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE



# Get links (need to put them in list; not easy to change with regex)

# links = ['http://www.espn.com/blog/nflnation/post/_/id/248390/week-2-nfl-predictions-scores-for-every-game']

links = ['http://www.espn.com/blog/nflnation/post/_/id/248390/week-2-nfl-predictions-scores-for-every-game', 'http://www.espn.com/blog/nflnation/post/_/id/249444/week-3-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/250507/week-4-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/251447/week-5-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/252472/week-6-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/253537/week-7-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/254530/week-8-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/255580/week-9-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/256669/week-10-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/257704/week-11-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/258633/week-12-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/259728/week-13-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/260725/week-14-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/261721/week-15-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/263010/week-16-nfl-predictions-scores-for-every-game',
'http://www.espn.com/blog/nflnation/post/_/id/264065/week-17-nfl-predictions-scores-for-every-game']



# url =
week = 1 # No stats for week 1, start at 1 and add
for link in links:
    url = link
    r = requests.get(url) #Get contents
    html = r.text # Get contents
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.findAll('p')
    week +=1
    for p in text:
        just = BeautifulSoup(str(p), "lxml").text
        if just[-1]!='.' and just[-1]!=')' and just.split()[-1]!='PickCenter' and just.split()[-3]=='--':
            justification = re.findall('(.*\.)', just)
            pundit = just.split()[-2] +' '+ just.split()[-1]
            score2 = just.split()[-4]
            team2 = just.split()[-5]
            if team2 == 'Francisco': # Week 6
                team2 ='49ers'
                score1 = just.split()[-7]
                score1 = int(score1.replace(',',''))
                team1 = just.split()[-8]
            else:
                score1 = just.split()[-6]
                score1 = int(score1.replace(',',''))
                team1 = just.split()[-7]
                team1 = team1.replace(',','') # one has comma
            if team1 == 'Bay':
                team1 = 'Bucs' # week 14 has Tampa Bay instead of Bucs

            cur.execute('''INSERT OR IGNORE INTO Predictions (week,
            pundit, team1,team2,score1,score2,just)
            Values (?,?,?,?,?,?,?)''', (week, pundit, team1, team2, score1, score2, justification[0]))

            conn.commit()
