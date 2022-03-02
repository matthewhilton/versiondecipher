# versiondecipher

WIP script / tool to work out what version of a plugin is installed on a Moodle site if there is no .git history. I.e. someone deleted git, or just copied and pasted code...

1. Clone main site to folder `main-repo` (or change variable `moodle_site_dir`)
2. Modify the variables `plugin_to_test` `plugin_dir` and `plugin_repository` accordingly.
3. Run the script: `python3 findcorehacksandversion.py`
4. Inspect the output. Look for the commit hash that has the least file changes. This is probably what is installed. Usually there is always 1 file change (the missing `.git` folder).
5. If all of them have significant file changes, there may be some modifications that have been made and has diverged from the original repository. Good luck! 😆

**This is a hacky script and is a WIP - use at your own risk!**
