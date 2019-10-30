# $ pip install PyGithub
# PyGithub documentation: https://buildmedia.readthedocs.org/media/pdf/pygithub/stable/pygithub.pdf


from github import Github
import pandas as pd
import os


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

repositories = g.search_repositories(query='language:python', sort='updated')
# query='good-first-issues:>3'     number of issues
for repo in repositories[1:10]:
    print(repo)
    print(repo.stargazers_count)

