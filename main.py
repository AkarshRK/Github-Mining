from github import Github
from collections import OrderedDict
from urllib2 import urlopen, Request 
import getpass
import javalang
import ast
import csv
import os

def download_url_content(url):
  token = "6589cc4152bbd974233939c5a5e71977cb9c8018"

  request = Request(url)
  request.add_header('Authorization', 'token %s' % token)
  response = urlopen(request)
  return response.read()

def get_str_method_signature(meth_name, parameters_list):
  method_sig = meth_name + " " + "( "
  for parameter in parameters_list:
      method_sig += parameter.type.name + " " + \
                    parameter.name + ", "
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
  csv_filename = '_'.join(repo_name.split('/')[-1]) + '.csv'
  report = []


  for index in range(1,70):
     print "Processing: ", index
     print "Latest commit msg: ", all_commits[index-1].commit.message, "\n"
     comp = repo.compare(all_commits[index].sha, all_commits[index-1].sha)

     for file in comp.files:
       if file.filename.split('.')[-1] == 'java':
          contents_url = file.contents_url
          try:
            # print "Content url: ", contents_url, "\n"
            content_info = download_url_content(contents_url)
          except:
            print "Can't read content_URL\n"
            continue
          dic = ast.literal_eval(content_info)

          prev_changes_url = "https://raw.githubusercontent.com/" + repo_name + \
                              "/" + all_commits[index].sha + "/" + dic['path']
          new_changes_url = "https://raw.githubusercontent.com/" + repo_name +  \
                            "/" + all_commits[index-1].sha + "/" + dic['path']

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
                      report.append([all_commits[index].sha, file.filename, old_meth_sig, new_meth_sig])                                 
            except:
              print "Bad java code\n"

  with open(abs_path + "/" + csv_filename, 'wb') as outcsv:
      writer = csv.writer(outcsv)
      writer.writerow(["Commit SHA", "Java File", "Old function signature", "New function signature"])
      for row in report:
        print "Report:  ", row, "\n"
        writer.writerow(row)


if __name__ == "__main__":
  main()