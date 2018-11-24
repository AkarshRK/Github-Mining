from github import Github
from collections import OrderedDict 
import getpass
import urllib2
import javalang
import ast

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
  repo_name = "AkarshRK/Java-Prog"
  repo = g.get_repo("AkarshRK/Java-Prog")
  all_commits = repo.get_commits()

  for index in range(1,len(list(all_commits))):
     print "Processing: ", index
     print "Latest commit msg: ", all_commits[index-1].commit.message, "\n"
     comp = repo.compare(all_commits[index].sha,all_commits[index-1].sha)
     for file in comp.files:
       contents_url = file.contents_url
       content_response = urllib2.urlopen(contents_url)
       content_info = content_response.read()
       dic = ast.literal_eval(content_info)

       prev_changes_url = "https://raw.githubusercontent.com/" + repo_name + \
                          "/" + all_commits[index].sha + "/" + dic['path']
       new_changes_url = "https://raw.githubusercontent.com/" + repo_name +  \
                         "/" + all_commits[index-1].sha + "/" + dic['path']

       file_read_success = False
       try:
         ver_one_response = urllib2.urlopen(prev_changes_url)
         ver_one_src_code = ver_one_response.read()

         ver_two_response = urllib2.urlopen(new_changes_url)
         ver_two_src_code = ver_two_response.read()
         file_read_success = True
       except urllib2.HTTPError, e:
         file_read_success = False

       if(file_read_success):
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

if __name__ == "__main__":
  main()