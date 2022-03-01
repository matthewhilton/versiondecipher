import subprocess
import os
import re
from termcolor import cprint, colored

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

# TODO in future, be able to give a CSV and iterate over it
# Test plugin
plugin_to_test = "mod_mediagallery"
plugin_dir = "mod/mediagallery" # TODO generate this automatically ?
plugin_repository = "https://github.com/open-lms-open-source/moodle-mod_mediagallery" # TODO if no repository, perhaps search via github API ?
moodle_site_dir = os.path.join(os.getcwd(), 'main-repo')
plugin_temp_dir = os.path.join(os.getcwd(), 'plugins_temp')
max_commit_searches = 1000

# Download the plugin files
test_plugin_dir = os.path.join(plugin_temp_dir, plugin_to_test)
moodle_installed_plugin_dir = os.path.join(moodle_site_dir, plugin_dir)

cprint("\nCloning {0} to {1}".format(plugin_to_test, test_plugin_dir), 'white', 'on_grey')
subprocess.run(["git clone {0} {1}".format(plugin_repository, test_plugin_dir)],text=True, shell=True)
subprocess.run(["cd {0} && git reset --hard origin".format(test_plugin_dir)],text=True, shell=True)

# Compare version.php
cloned_versionphp_filedir = os.path.join(test_plugin_dir, 'version.php')
moodle_versionphp_filedir = os.path.join(moodle_installed_plugin_dir, 'version.php')

cprint("\nExamining version.php for each commit hash.", 'white', 'on_grey')
matching_commit_hashes = []
for i in range(max_commit_searches):
        current_git_hash = subprocess.run(["cd {0} && git rev-parse HEAD".format(test_plugin_dir)], text=True, shell=True, capture_output=True).stdout.rstrip()

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
print("If the only diff here is .git, it is likely the exact same code.")
for commitchange in files_changed:
    cprint("{0} - {1}".format(commitchange[0], commitchange[1]), 'cyan')

cprint("\nDone", "white", "on_grey")
