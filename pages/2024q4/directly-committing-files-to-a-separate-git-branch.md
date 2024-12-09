+++
published = 2024-12-09
description = "Committing specific files to a separate git branch without perturbing your current git state"
+++

# Directly committing files to a separate git branch

Suppose you have some files you want to directly commit to a branch in your
current git repository, doing so without perturbing your current branch. Why
would you want to do that? My current motivating use case is to commit all my
draft muxup.com posts to a separate branch so I can get some tracking and
backups without needing to add WIP work to the public repo. But I also use
essentially the same approach to make a throw-away commit of the current repo
state (including any non-staged or non-committed changes) to be pushed to a
remote machine for building.

Our goal is to create a commit, so a sensible starting point is to break down
what's involved. Referring to Git
[documentation](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) we
can break down the different object types that we need to put together a
commit:
* A commit object contains metadata as well as a reference a tree
object.
* A tree object is essentially a list of blob objects and other tree
objects with extra metadata such as name and permissions.
* A blob object is a chunk of data (e.g. a file).

Although it's possible to build a tree
object semi-manually using `git hash-object` to create blobs and `git mktree`
for trees, fortunately this isn't necessary. Using a throwaway git index file
allows us to rely on git to create the tree object for us after indicating the
files to be included. The basic approach is:
* Identify the files you wish to commit.
* Set the `GIT_INDEX_FILE` environment variable to a throwaway/temporary name.
* Add the files to the temporary index (`git update-index` is the 'plumbing'
  way of doing this, but `git add` can work just fine as well).
* Create a tree object from the index using `git write-tree`.
* Create a commit object with an appropriate commit message and parent.
  * You likely want to bail out and avoid creating a commit that changes no
    files if it turns out the tree is unmodified vs the parent commit.
* Use `git update-ref` to update the branch ref to point to the new commit.
* Remove the temporary index file.

## Implementation in Python

Here is how I implemented this in the [site generator I use for
muxup.com](https://github.com/muxup/muxup-site/blob/main/gen):

```python
def commit_untracked() -> None:
    def exec(*args: Any, **kwargs: Any) -> tuple[str, int]:
        kwargs.setdefault("encoding", "utf-8")
        kwargs.setdefault("capture_output", True)
        kwargs.setdefault("check", True)

        result = subprocess.run(*args, **kwargs)
        return result.stdout.rstrip("\n"), result.returncode

    result, _ = exec(["git", "status", "-uall", "--porcelain", "-z"])
    untracked_files = []
    entries = result.split("\0")
    for entry in entries:
        if entry.startswith("??"):
            untracked_files.append(entry[3:])

    if len(untracked_files) == 0:
        print("No untracked files to commit.")
        return

    bak_branch = "refs/heads/bak"
    show_ref_result, returncode = exec(
        ["git", "show-ref", "--verify", bak_branch], check=False
    )
    if returncode != 0:
        print("Branch {back_branch} doesn't yet exist - it will be created")
        parent_commit = ""
        parent_commit_tree = None
        commit_message = "Initial commit of untracked files"
        extra_write_tree_args = []
    else:
        parent_commit = show_ref_result.split()[0]
        parent_commit_tree, _ = exec(["git", "rev-parse", f"{parent_commit}^{{tree}}"])
        commit_message = "Update untracked files"
        extra_write_tree_args = ["-p", parent_commit]

    # Use a temporary index in order to create a commit. Add any untracked
    # files to the index, create a tree object based on the index state, and
    # finally create a commit using that tree object.
    temp_index = pathlib.Path(".drafts.gitindex.tmp")
    atexit.register(lambda: temp_index.unlink(missing_ok=True))
    git_env = os.environ.copy()
    git_env["GIT_INDEX_FILE"] = str(temp_index)
    nul_terminated_untracked_files = "\0".join(file for file in untracked_files)
    exec(
        ["git", "update-index", "--add", "-z", "--stdin"],
        input=nul_terminated_untracked_files,
        env=git_env,
    )
    tree_sha, _ = exec(["git", "write-tree"], env=git_env)
    if tree_sha == parent_commit_tree:
        print("Untracked files are unchanged vs last commit - nothing to do.")
        return
    commit_sha, _ = exec(
        ["git", "commit-tree", tree_sha] + extra_write_tree_args,
        input=commit_message,
    )
    exec(["git", "update-ref", bak_branch, commit_sha])

    diff_stat, _ = exec(["git", "show", "--stat", "--format=", commit_sha])

    print(f"Backup branch '{bak_branch}' updated successfully.")
    print(f"Created commit {commit_sha} with the following modifications:")
    print(diff_stat)
```

For my particular use case, creating a commit containing _only_ the untracked
files is what I want. I'm happy to lose the ability to precisely recreate
the repository state for the combination of tracked and untracked files in
return for avoiding noise in the changes for the `bak` branch that would
otherwise be present from changes to tracked files. Using paths separated by
`NUL` via stdin is overkill here, but as it doesn't increase complexity of the
code much, I've opted for the most universal approach in case I copy the logic
to other projects.

