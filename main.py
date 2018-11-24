from github import Github
from collections import OrderedDict
from urllib2 import urlopen, Request 
import getpass
import javalang
import csv
import os

def download_url_content(url):
  # removed token for commit purpose
  token = ""

  request = Request(url)
  request.add_header('Authorization', 'token %s' % token)
  response = urlopen(request)
  return response.read()

def get_str_method_signature(meth_name, parameters_list):
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
  user = "akarshrain@gmail.com"
  pswd = getpass.getpass("Password?")
  g = Github(user, pswd)
  repo_name = "TheAlgorithms/Java"
  repo = g.get_repo(repo_name)
  all_commits = repo.get_commits()
  abs_path = os.path.abspath("report")

  outcsv = open(abs_path + "/" + "report.csv", 'wb')
  writer = csv.writer(outcsv)
  writer.writerow(["Commit SHA", "Java File", "Old function signature", "New function signature"])

  for index in range(1,len(list(all_commits))):
     print "Processing: ", index
     #print "Latest commit msg: ", all_commits[index-1].commit.message, "\n"
     comp = repo.compare(all_commits[index].sha, all_commits[index-1].sha)

     for file in comp.files:
       if file.filename.split('.')[-1] == 'java':

          prev_changes_url = "https://raw.githubusercontent.com/" + repo_name + \
                              "/" + all_commits[index].sha + "/" + file.filename
          new_changes_url = "https://raw.githubusercontent.com/" + repo_name +  \
                            "/" + all_commits[index-1].sha + "/" + file.filename

          file_read_success = False
          try:
            ver_one_src_code = download_url_content(prev_changes_url)
            ver_two_src_code = download_url_content(new_changes_url)
            file_read_success = True
          except:
            file_read_success = False

          if(file_read_success):
            print "File read successful\n"
            try:
              old_syntax_tree = javalang.parse.parse(ver_one_src_code)
              new_syntax_tree = javalang.parse.parse(ver_two_src_code)

              old_methods_data = OrderedDict()

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
                      writer.writerow([all_commits[index].sha, file.filename, old_meth_sig, new_meth_sig])

            except:
              print "Bad java code\n"


if __name__ == "__main__":
  main()