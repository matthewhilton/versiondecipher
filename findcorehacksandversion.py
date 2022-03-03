import subprocess
import os
import re
from termcolor import cprint, colored
import argparse
from simple_term_menu import TerminalMenu

# Extract version from version.php
def get_versionphp_version(filedir):
    # Read file
    with open(filedir) as versionfile:
        data = versionfile.read()
        #print(data)

        # Run regex to find line
        pattern = re.compile(r'^.*plugin->version.*$', re.MULTILINE)
        match = pattern.findall(data)

        if(len(match) == 0):
            # Try using $module rather than $plugin
            pattern2 = re.compile(r'^.*module->version.*$', re.MULTILINE)
            match = pattern2.findall(data)

            # Still no match found!
            if(len(match) == 0):
                return None

        # Cleanup
        version = "".join(filter(str.isdigit, match[0]))

        # Return version
        return version

# Setup CLI args
parser = argparse.ArgumentParser(description='Find core hacks and version of plugin as submodule.')

parser.add_argument('--plugin', type=str, required=True,
                    help='plugin name to test. e.g. block_turnitin')

parser.add_argument('--dir', type=str, required=True,
                    help='plugin directory to test. e.g. blocks/turnitin')

parser.add_argument('--repository', type=str, required=True,
                    help='plugin repository. e.g. https://github.com/turnitin/moodle-block_turnitin')

parser.add_argument('--branch', type=str, required=True,
                    help='plugin branch. e.g. master')

args = parser.parse_args()

# TODO cleaup variables.
plugin_to_test = args.plugin
plugin_dir = args.dir
plugin_repository = args.repository
branch = args.branch
moodle_site_default_branch = "catalyst-main"
moodle_site_dir = os.path.join(os.getcwd(), 'main-repo')
plugin_temp_dir = os.path.join(os.getcwd(), 'plugins_temp')
max_commit_searches = 1000

if('http' in plugin_repository):
    cprint("\nError - use the git@ url instead of HTTPs URL.", 'red', 'on_grey', attrs=["bold"])
    exit()

# Download the plugin files
test_plugin_dir = os.path.join(plugin_temp_dir, plugin_to_test)
moodle_installed_plugin_dir = os.path.join(moodle_site_dir, plugin_dir)

cprint("\nCloning {0} to {1}".format(plugin_to_test, test_plugin_dir), 'white', 'on_grey')
subprocess.run(["git clone {0} -b {2} {1}".format(plugin_repository, test_plugin_dir, branch)],text=True, shell=True)
subprocess.run(["cd {0} && git fetch && git reset --hard origin".format(test_plugin_dir)],text=True, shell=True)

# Compare version.php
cloned_versionphp_filedir = os.path.join(test_plugin_dir, 'version.php')
moodle_versionphp_filedir = os.path.join(moodle_installed_plugin_dir, 'version.php')

cprint("\nExamining version.php for each commit hash.", 'white', 'on_grey')
matching_commit_hashes = []
for i in range(max_commit_searches):
        current_git_hash = subprocess.run(["cd {0} && git rev-parse HEAD".format(test_plugin_dir)], text=True, shell=True, capture_output=True).stdout.rstrip()

        # No more commits to rollback
        if current_git_hash in matching_commit_hashes:
            break;

        cloned_version = get_versionphp_version(cloned_versionphp_filedir);
        moodle_version = get_versionphp_version(moodle_versionphp_filedir);
        versions_match = moodle_version == cloned_version
        print("{0} at {4} - moodle: {1}, Remote: {2} - Same? {3}".format(plugin_dir, moodle_version, cloned_version, colored(versions_match, 'green' if versions_match else 'red'), current_git_hash))

        if(versions_match):
            matching_commit_hashes.append(current_git_hash)

        if(cloned_version < moodle_version):
            break;

        # Rollback 1 commit
        output = subprocess.run(["cd {0} && git checkout HEAD~1".format(test_plugin_dir)], stderr=subprocess.PIPE, text=True, shell=True)

if(len(matching_commit_hashes) == 0):
    print("No matching commits found, and remote version was lower than installed. Wrong branch or diverged ?")
    exit()

# Record the diff no for each hash
files_changed = []

cprint("\nSwitching remote site to default branch", 'cyan', 'on_grey', attrs=["bold"])
subprocess.run(["cd {0} && git switch {1} --force".format(moodle_site_dir, moodle_site_default_branch)], stderr=subprocess.PIPE, text=True, shell=True)

# Found matching versions, see the diffs of each
for hash in matching_commit_hashes:
    cprint("\nComparing Moodle site plugin and Remote repository code at remote commit hash {0}".format(hash), 'cyan', 'on_grey', attrs=["bold"])
    command = "cd {0} && git checkout {1} && diff {2} {3} | diffstat".format(test_plugin_dir, hash, moodle_installed_plugin_dir, test_plugin_dir); # Cant use git-diff here else .git directory messes it up!

    gitdiff = subprocess.run([command], shell=True, capture_output=True, text=True)
    output = gitdiff.stdout.splitlines()

    for line in output:
        print(line)
    
    cprint("\nTo recreate, run:", 'cyan', attrs=["bold"])
    print("\n" + command + "\n")
    
    files_changed.append([hash, output[-1]])

# Print files changed summary
cprint("\nCommit hash change summary:", "white", "on_grey")
print("These commits have the same version.php value, but still may have different files or custom hacks.")
print("If the only diff here is .git, it is likely the exact same code (just missing the hidden .git file!).")
for commitchange in files_changed:
    cprint("{0} - {1}".format(commitchange[0], commitchange[1]), 'cyan')

cprint("\nDone", "white", "on_grey")

# Menu to select hash, then move to add as a submodule
options = matching_commit_hashes

cprint("Select hash to add a submodule, or Ctrl+C to cancel", "green")
terminal_menu = TerminalMenu(options)
menu_entry_index = terminal_menu.show()

if(menu_entry_index is None):
    exit();
else:
    selected_hash = options[menu_entry_index]
    print("Selected {0}".format(selected_hash))
    # Generate command to add as submodule.
    nextcmd = "python3 makesubmodulefromhash.py --plugin {0} --dir {1} --repository {2} --branch {3} --hash {4}".format(args.plugin, args.dir, args.repository, args.branch, selected_hash)
    
    cprint("To add hash as submodule easily, run the following:", 'green')
    print(nextcmd)