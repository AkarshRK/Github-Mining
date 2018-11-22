from github import Github
import getpass
import urllib2
import re

def main():
  user = "akarshrain@gmail.com"
  pswd = getpass.getpass("Password?")
  g = Github(user, pswd)
  repo = g.get_repo("AuthorizeNet/sample-code-java")
  all_commits = repo.get_commits()

  for index in range(1,len(list(all_commits))):
     print "Processing: ", index
     comp = repo.compare(all_commits[index].sha,all_commits[index-1].sha)
     response = urllib2.urlopen(comp.diff_url)
     diff = response.read()
     m = re.findall(r'(?=([+\s*](public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])))',diff)
     if(m):
       print m[0][0]


if __name__ == "__main__":
  main()