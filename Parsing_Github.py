# $ pip install PyGithub
# PyGithub documentation: https://buildmedia.readthedocs.org/media/pdf/pygithub/stable/pygithub.pdf


from github import Github
import pandas as pd
import os

#api_key=open('api_key.txt','r').read()
#access_token=open('access_token.txt','r').read().strip()
g = Github("alexanu", "XXXX")

#-------- Parsing my repos --------------------------------------------------------------

ID_my=[]
Parent_name=[]
Parent_id=[]
Parent_update=[]
descr_my=[]
Repo_source=[]
created_my=[]
size_my=[]
own_repo = "Own repo"

for repo in g.get_user().get_repos(): # going throung my repos
    ID_my.append(repo.id)
    if repo.parent is None: # if the repo is mine (i.e. no parent)
        Parent_name.append(repo.name)
        Parent_id.append(repo.id)
        Parent_update.append(repo.updated_at)
        Repo_source.append("Own")
    else:
        Parent_name.append(repo.parent.full_name)
        Parent_id.append(repo.parent.id)
        Parent_update.append(repo.parent.updated_at)
        Repo_source.append("Forked")
    descr_my.append(repo.description)
    created_my.append(repo.created_at)
    size_my.append(repo.size)
    
for repo in g.get_user().get_starred(): # going through starred repos
    ID_my.append(repo.id)
    Parent_name.append(repo.name)
    Parent_id.append(repo.id) # the same as ID_my
    Parent_update.append(repo.updated_at)
    Repo_source.append("Star")
    descr_my.append(repo.description)
    created_my.append(repo.created_at)
    size_my.append(repo.size)
    
my_repos = pd.DataFrame({'My_ID': ID_my,
                         'Source': Repo_source,
                        'Parent': Parent_name,
                        'Parent_ID': Parent_id,
                        'Parent_Update': Parent_update,
                        'Created': created_my,
                        'Size': size_my,
                        'Descrip': descr_my,
						})

my_repos.to_csv("Repos.csv")

#-------- Searching Github --------------------------------------------------------------

# https://python.gotrained.com/search-github-api/

keywords = "IEX, hedge, oanda, quandl, NYSE, FIX, ETF, " \
            "market calendar, equity, kelly, arbitrage, backtest, " \
            "quant, EDGAR, SEC, del Prado, zorro trading"
keyword = [keyword.strip() for keyword in keywords.split(',')]

exclude_keywords = "ng-zorro, ngx-zorro, ngzorro, CSS, Typescript"
exclude_keyword = [keyword.strip() for keyword in exclude_keywords.split(',')]

query = '+'.join(keyword) + '+NOT'+ '+'.join(exclude_keyword)+'pushed:>=2019-07-05'+'language:python' +'+in:readme+in:description'
result = g.search_repositories(query, 'stars', 'desc')
print(f'Found {result.totalCount} repo(s)')

for repo in result:
    print(f'{repo.clone_url}, {repo.stargazers_count} stars')


repositories = g.search_repositories(query='language:python', sort='updated')
# query='good-first-issues:>3'     number of issues
for repo in repositories[1:10]:
    print(repo)
    print(repo.stargazers_count)

# ---------------------------------------------------------------------------------------

def search_github(keywords):
    query = '+'.join(keywords) + '+in:readme+in:description' # '+in:readme+in:description'  are the qualifiers
    result = g.search_repositories(query, 'stars', 'desc')

    print(f'Found {result.totalCount} repo(s)')

    for repo in result:
        print(f'{repo.clone_url}, {repo.stargazers_count} stars')

search_github(keyword)
