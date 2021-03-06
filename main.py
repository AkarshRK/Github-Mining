from github import Github
from collections import OrderedDict
from urllib2 import urlopen, Request, HTTPError
from datetime import datetime
import time
import getpass
import javalang
import csv
import os
import re

def get_valid_filename(repo_name):
  '''
     Input: repository name (string)
     Returns: a valid file name created from the input string 
  '''
  # Remove invalid characters
  valid_filename = re.sub('[^0-9a-zA-Z_]', '', repo_name)

  # Remove leading characters until we find a letter or underscore
  valid_filename = re.sub('^[^a-zA-Z_]+', '', valid_filename)

  return valid_filename

def check_ratelimit(git_instance):
  '''
     An user is granted 5000 api requests per hour. This function checks 
     the rate limit of GitHub api(s) remaining for a given user. If at all
     the remaining rate limit reaches 0 within the alloted hour, then the
     function halts the program by going into sleep mode until the rate 
     limit is restored.[A VERY RARE CASE]
     
     Note: I have used this function to be on the safer side if in case
           the rate limit reaches as low as 10.
  '''
  remaining, total = git_instance.rate_limiting
  print "You have ", remaining, " api request\n" 
  if remaining < 10:
   reset_time = datetime.fromtimestamp(git_instance.rate_limiting_resettime)
   current_time = datetime.utcnow()
   total_wait_seconds = (reset_time - current_time).total_seconds()
   if total_wait_seconds>0:
    print "Total seconds to wait: ", total_wait_seconds
    time.sleep(total_wait_seconds)

def get_url(repo_name, commit_sha, file_path):
  return "https://raw.githubusercontent.com/" + repo_name + \
         "/" + commit_sha + "/" + file_path


def download_url_content(url):
   '''
      This function downloads the Java source code at a 
      specific commit point.
   '''
   # removed token for commit purpose
   token = "<token>"

   request = Request(url)
   request.add_header('Authorization', 'token %s' % token)
   response = urlopen(request)
   return response.read()

def get_str_method_signature(meth_name, parameters_list):
  '''
     This function returns the signature of a method found in
     MethodDeclaration object in string format.
  '''
  method_sig = meth_name + " " + "( "
  for parameter in parameters_list:
      parameter_type = parameter.type
      dimension = '[]'*len(parameter_type.dimensions)
      method_sig += parameter.type.name + " " + \
                    dimension + " " + \
                    parameter.name + ", "
  if(len(parameters_list)>0):
    method_sig = method_sig[:-2]
  method_sig += " )"
  return method_sig

def main():
  user = raw_input("Enter your email address:")
  pswd = getpass.getpass("Enter Password:")
  g = Github(user, pswd)

  with open("repositories.txt") as f:
    repositories = f.readlines()

  repositories = [x.strip() for x in repositories]

  for repo_name in repositories:
    print "Analyzing: ", repo_name, "\n"
    try: 
     repo = g.get_repo(repo_name)
    except:
     print "Invalid repository name"
     continue
    all_commits = repo.get_commits()
    abs_path = os.path.abspath("report")
    valid_filename = get_valid_filename(repo_name)

    outcsv = open(abs_path + "/" + valid_filename + ".csv", 'wb')
    writer = csv.writer(outcsv,  delimiter=',', dialect='excel')
    writer.writerow(["Commit SHA", "Java File", "Old function signature", "New function signature"])
    total_commits = len(list(all_commits))


    for index in range(1, total_commits):
       check_ratelimit(g)
       print "Processing commit ", index, " of ", total_commits 
       try:
        comp = repo.compare(all_commits[index].sha, all_commits[index-1].sha)
       except:
         '''
            Here, there can be error(s) in comparing two commits due to following reasons:
            1. A file was deleted in the new commit
            2. There was no common ancestor for the two commits
            
            The above two errors can be ignored as it is not relevant to us and does not affect
            the goal of the intended task.
         '''
         print "Error in comparing commit"
         continue

       for file in comp.files:
         if file.filename.split('.')[-1] == 'java':

            prev_changes_url = get_url(repo_name, all_commits[index].sha, file.filename)
            new_changes_url = get_url(repo_name, all_commits[index-1].sha, file.filename)

            file_read_success = False
            try:
              ver_one_src_code = download_url_content(prev_changes_url)
              ver_two_src_code = download_url_content(new_changes_url)
              file_read_success = True
            except:
              file_read_success = False

            if(file_read_success):
              try:
                '''
                   Here, an Abstract Syntax Tree is generated for each version 
                   of the Java source code using javalang parser.
                '''
                old_syntax_tree = javalang.parse.parse(ver_one_src_code)
                new_syntax_tree = javalang.parse.parse(ver_two_src_code)

                old_methods_data = OrderedDict()
                print "Java source code parsed successfully\n"

                for path, node in old_syntax_tree.filter(javalang.tree.MethodDeclaration):
                  old_methods_data[node.name] = {
                    'no_of_parameters': len(node.parameters),
                    'method_node': node
                  }
          
                for path, node in new_syntax_tree.filter(javalang.tree.MethodDeclaration):
                  if node.name in old_methods_data:
                    if len(node.parameters) > old_methods_data[node.name]['no_of_parameters']:
                      print "Warning: Parameter count increased in ", node.name, "\n"
                      new_meth_sig = get_str_method_signature(node.name, node.parameters)
                      old_meth_sig = get_str_method_signature(node.name, old_methods_data[node.name]['method_node'].parameters)
                      print "Old Signature: ", old_meth_sig, "\n"
                      print "New Signature: ", new_meth_sig, "\n"
                      writer.writerow([all_commits[index-1].sha, file.filename, old_meth_sig, new_meth_sig])
              except:
                print "Bad java source code\n"


if __name__ == "__main__":
  main()
