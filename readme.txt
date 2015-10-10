Git is free software.

Quick setup — if you’ve done this kind of thing before
or

We recommend every repository include a README, LICENSE, and .gitignore.
…or create a new repository on the command line

echo # learnpython >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/karisdong/learnpython.git
git push -u origin master

…or push an existing repository from the command line

git remote add origin https://github.com/karisdong/learnpython.git
git push -u origin master

…or import code from another repository

You can initialize this repository with code from a Subversion, Mercurial, or TFS project.

------------------------------------------------

git add readme.txt
git status
git commit -m "git tracks changes"