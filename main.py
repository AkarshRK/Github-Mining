from github import Github, Repository, Commit
import getpass

def main():
  user = "akarshrain@gmail.com"
  pswd = getpass.getpass("Password?")
  g = Github(user,pswd)
  repo = g.get_repo("AkarshRK/Maze-Game---OpenGL")
  all_commits = repo.get_commits()
  for commit in all_commits:
    print commit

if __name__ == "__main__":
  main()