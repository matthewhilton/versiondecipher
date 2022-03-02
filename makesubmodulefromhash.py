
import subprocess
import os
from termcolor import cprint, colored
import argparse

# CLI args
parser = argparse.ArgumentParser(description='Find core hacks and version of plugin as submodule.')

parser.add_argument('--plugin', type=str, required=True,
                    help='plugin name to test. e.g. block_turnitin')

parser.add_argument('--dir', type=str, required=True,
                    help='plugin directory to test. e.g. blocks/turnitin')

parser.add_argument('--repository', type=str, required=True,
                    help='plugin repository. e.g. https://github.com/turnitin/moodle-block_turnitin')

parser.add_argument('--branch', type=str, required=True,
                    help='plugin branch. e.g. master')

parser.add_argument('--hash', type=str, required=True,
                    help='hash to checkout')     

args = parser.parse_args()

### Config

# TODO cleanup
plugin_name = args.plugin
plugin_dir = args.dir
git_repo = args.repository
branch = args.branch
commit_hash = args.hash
site_folder = "main-repo"

####

site_dir = os.path.join(os.getcwd(), site_folder)

# Go into repo and checkout working branch
cprint("\nChecking out branch", 'cyan', 'on_grey')
subprocess.run(["cd {0} && git reset --hard origin && git checkout --force -b WR375472-move-{1}-to-submodule".format(site_dir, plugin_name)],text=True, shell=True)

# Delete the current code
cprint("\nDeleting existing code & submodule cache", 'cyan', 'on_grey')
plugin_path = os.path.join(site_dir, plugin_dir)
subprocess.run(["rm -rf {0}".format(plugin_path)],text=True, shell=True)
subprocess.run(["cd {0} && git rm -rf --cache {1}".format(site_dir, plugin_dir)],text=True, shell=True)

# Add submodule
cprint("\nAdding as submodule",'cyan', 'on_grey')
command = "cd {0} && git submodule add -b {3} --force {1} {2}".format(site_dir, git_repo, plugin_dir, branch)
print(command)
subprocess.run([command],text=True, shell=True)

# Go to submodule path and checkout the commit hash
cprint("\nChecking out the correct hash", 'cyan', 'on_grey')
output = subprocess.run(["cd {0} && git checkout -f {1}".format(plugin_path, commit_hash)],text=True, shell=True)
if(output.returncode != 0):
    cprint('Error checking out commit. Stopping script.', 'red')
    exit()

# Add the new submodule hash path to the commit
cprint("\nAdding submodule hash to commit", 'cyan', 'on_grey')
subprocess.run(["cd {0} && git add {1}".format(site_dir, plugin_dir)],text=True, shell=True)

cprint("\nSorting submodules file", 'cyan', 'on_grey')
subprocess.run(["bash sortgitmodules.sh && cd {0} && git add .gitmodules".format(site_dir)], text=True, shell=True)

# Make commit
cprint("\nComitting changes", 'cyan', 'on_grey')
subprocess.run(["cd {0} && git commit -m \"WR375472 moved {1} to submodule\"".format(site_dir, plugin_name)],text=True, shell=True)