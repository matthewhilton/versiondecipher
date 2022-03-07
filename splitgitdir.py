import subprocess
import os
from termcolor import cprint, colored
import argparse
from simple_term_menu import TerminalMenu

# CLI args
parser = argparse.ArgumentParser(description='Find core hacks and version of plugin as submodule.')

parser.add_argument('--comparisonsite', type=str, required=True,
                    help='Base site to compare plugin code to')

parser.add_argument('--plugin', type=str, required=True,
                    help='plugin name to test. e.g. block_turnitin')

parser.add_argument('--dir', type=str, required=True,
                    help='plugin directory to test. e.g. blocks/turnitin')

parser.add_argument('--repository', type=str, required=True,
                    help='plugin repository. e.g. https://github.com/turnitin/moodle-block_turnitin')

args = parser.parse_args()

# Config
comparison_repo_folder = args.comparisonsite
temp_plugin_folder = "plugin-own-repo"
remote_repo = args.repository
plugin_dir = args.dir
branch_naming = "WR375472-migrate-{0}-to-own-repository"
plugin = args.plugin

# Generated config
temp_plugin_dir = os.path.join(os.getcwd(), temp_plugin_folder)
comparison_site_dir = os.path.join(os.getcwd(), comparison_repo_folder)
plugin_folder_in_site_dir = os.path.join(os.getcwd(), comparison_repo_folder, plugin_dir)
branch_name = branch_naming.format(plugin)

# Delete existing temp code
cprint("\nDeleting temp dir", 'white', 'on_grey')
subprocess.run(["rm -rf {0}".format(temp_plugin_dir)], text=True, shell=True)

# Copy the untouched version
cprint("\nCopying site to temp dir", 'white', 'on_grey')
subprocess.run(["cp -r {0} {1}".format(comparison_repo_folder, temp_plugin_folder)], text=True, shell=True)

# Run git filter-dir
cprint("\nFiltering subdirectory", 'white', 'on_grey')
subprocess.run(["cd {0} && git filter-repo --subdirectory-filter {1}".format(temp_plugin_dir, plugin_dir)], text=True, shell=True)

# Diff to check - add confirm dialog
cprint("\nDiff check", 'white', 'on_grey')
subprocess.run(["diff -r {0} {1} | diffstat".format(temp_plugin_dir, plugin_folder_in_site_dir)], text=True, shell=True)

# Wait for confirmation
cprint("\nIs this diff correct?", 'cyan', 'on_grey')
terminal_menu = TerminalMenu(["yes", "no"])
menu_entry_index = terminal_menu.show()

if(menu_entry_index is not 0):
    exit()

# Add gitlab remote
cprint("\nAdding remote to repository", 'white', 'on_grey')
subprocess.run(["cd {0} && git remote add origin {1}".format(temp_plugin_dir, remote_repo)], text=True, shell=True)

# Checkout branch
cprint("\nChecking out branch", 'white', 'on_grey')
subprocess.run(["cd {0} && git checkout -b {1}".format(temp_plugin_dir, branch_name)], text=True, shell=True)

# Push branch to upstream
cprint("\nPushing branch to remote", 'white', 'on_grey')
subprocess.run(["cd {0} && git push --set-upstream origin {1}".format(temp_plugin_dir, branch_name)], text=True, shell=True)