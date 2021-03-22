# The tools

You'll need [NOWEB](https://www.cs.tufts.edu/~nr/noweb/) to compile the source 
to Python. (Or to compile the source to TeX for documentation.)

Once you have that, you clone the repo and recurse through submodules. Either
```bash
git clone --recurse-submodules
```
or
```bash
git clone [...]
git submodule --update --init --recursive
```

# Working with the source

The main parts for the documentation is located in `/doc`. These files are 
documentation only files. To compile the documentation, go to `/doc` and run 
`make all`.

The package source code is located in `/src/ladok3`. These files contains both 
the Python code and the documentation for the code. To compile the Python 
package, go to `/src/ladok3` and run `make all`.

Alternatively, one can run `make all` in the root to build both. `make install` 
will run `pip install -e .`. This is useful for development.


# Workflow

Please [fork the repository][ForkARepo], make your changes, commit them and 
then create a [pull request][PullRequest] in the original repository.

[ForkARepo]: https://help.github.com/articles/fork-a-repo/
[PullRequest]: https://help.github.com/articles/using-pull-requests/

