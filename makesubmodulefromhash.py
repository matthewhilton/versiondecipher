
import subprocess
import os
from termcolor import cprint, colored

### Config

plugin_name = "mod_mediagallery"
plugin_dir = "mod/mediagallery"
git_repo = "https://github.com/open-lms-open-source/moodle-mod_mediagallery"
branch = "master"
commit_hash = "df6c3b375dce0553a85fb85f707ebe1c25c7ef20"
site_folder = "main-repo"

####

site_dir = os.path.join(os.getcwd(), site_folder)

# Go into repo and checkout working branch
cprint("\nChecking out branch", 'cyan', 'on_grey')
subprocess.run(["cd {0} && git reset --hard origin && git checkout -b WR375472-move-{1}-to-submodule".format(site_dir, plugin_name)],text=True, shell=True)

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
subprocess.run(["cd {0} && git checkout -f {1}".format(plugin_path, commit_hash)],text=True, shell=True)

# Add the new submodule hash path to the commit
cprint("\nAdding submodule hash to commit", 'cyan', 'on_grey')
subprocess.run(["cd {0} && git add {1}".format(site_dir, plugin_dir)],text=True, shell=True)

# Make commit
cprint("\nComitting changes", 'cyan', 'on_grey')
subprocess.run(["cd {0} && git commit -m \"WR375472 moved {1} to submodule\"".format(site_dir, plugin_name)],text=True, shell=True)