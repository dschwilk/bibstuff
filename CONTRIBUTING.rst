Contributing to bibstuff
========================

Using the issue tracker
-----------------------

The issue tracker is the preferred channel for bug reports, 
features requests and pull requests.

Bug reports
-----------

A bug is a *demonstrable problem* that is caused by the code in the
repository. Good bug reports are extremely helpful - thank you!

Guidelines for bug reports:
 * **Use the GitHub issue search** — check if the issue has already
   been reported.

 * **Check if the issue has been fixed** — try to reproduce it using
   the latest ``master`` or development branch in the repository.

 * **Isolate the problem** — create a reduced test case and a live 
   example.

Feature requests
----------------

Feature requests are welcome.

[TODO]

Pull requests
-------------

Coding conventions
~~~~~~~~~~~~~~~~~~

#. Python code in bibstuff is indented with tabs.
#. Use the numpy reStructured text format for docstrings: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Contributing via a pull request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `Fork <http://help.github.com/fork-a-repo/>`__ the project, clone your fork,
   and configure the remotes::

        # Clone your fork of the repo into the current directory
        git clone https://github.com/<your-username>/bibstuff
        # Navigate to the newly cloned directory
        cd bibstuff
        # Assign the original repo to a remote called "upstream"
        git remote add upstream https://github.com/dschwilk/bibstuff

2. If you cloned a while ago, get the latest changes from upstream::

        git checkout <dev-branch>
        git pull upstream <dev-branch>

3. Create a new topic branch (off the main project development branch) to
   contain your feature, change, or fix::

      git checkout -b <topic-branch-name>

4. Commit your changes in logical chunks. Use Git's 
   `interactive rebase <https://help.github.com/articles/interactive-rebase>`__ 
   feature to tidy up your commits before making them public. The commit message
   should conform to the description at
   http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html

5. Test your code, add tests to the /tests folder
   
5. Locally merge (or rebase) the upstream development branch into your
   topic branch::

      git pull [--rebase] upstream <dev-branch>

6. Push your topic branch up to your fork::

       git push origin <topic-branch-name>

7. `Open a Pull Request <https://help.github.com/articles/using-pull-requests/>`__ 
   with a clear title and description.
