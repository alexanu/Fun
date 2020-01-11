from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime

mainURL = "https://deepindex.org/"

topic = []
size=[]
projects=[]
groups =[]

page = urlopen(mainURL)
soup = bs(page)
topics = soup.find_all('h3')
for topic in topics:
	project = topic.find('p').text
	projects.append(project)
	groups.append(topic)

deep = pd.DataFrame({'Category': groups,
					 'Projects': projects
						})

deep['Status'] = str(datetime.date.today()) # new column: when the query was done


#--------------------------------------------------------------------------------------

topics = []
topics = soup.find_all("div", class_="col-md-4")
for topic in topics:
    print(topic.find('p').text)


