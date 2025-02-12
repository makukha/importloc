default:
    @just --list

# helpers
git-head := "$(git rev-parse --abbrev-ref HEAD)"
gh-issue := "$(git rev-parse --abbrev-ref HEAD | cut -d- -f1)"
gh-title := "$(GH_PAGER=cat gh issue view " + gh-issue + " --json title -t '{{.title}}')"
version := "$(uv run bump-my-version show current_version 2>/dev/null)"

# init local dev environment
[group('dev')]
[macos]
init:
    #!/usr/bin/env bash
    set -euo pipefail
    sudo port install gh uv yq
    just sync
    # pre-commit hook
    echo -e "#!/usr/bin/env bash\njust pre-commit" > .git/hooks/pre-commit
    chmod a+x .git/hooks/pre-commit
# synchronize local dev environment
[group('dev')]
sync:
    uv sync --all-extras --all-groups

# upgrade versions
[group('dev')]
upd:
    uv sync --all-extras --all-groups --upgrade

# add news item
[group('dev')]
news type issue *msg:
    #!/usr/bin/env bash
    set -euo pipefail
    issue="{{ if issue == "-" { gh-issue } else { issue } }}"
    msg="{{ if msg == "" { gh-title } else { msg } }}"
    uv run towncrier create -c "$msg" "$issue.{{type}}.md"
# run checkers
[group('dev')]
lint:
    uv run mypy .
    uv run ruff check
    uv run ruff format --check

# build python package
[group('dev')]
build: sync
    make build

# run tox tests
[group('dev')]
test *toxargs: build
    time docker compose run --rm -it tox \
        {{ if toxargs == "" { "run-parallel" } else { "run" } }} \
        --installpkg="$(find dist -name '*.whl')" {{toxargs}}

# enter testing container
[group('dev')]
shell:
    docker compose run --rm -it --entrypoint bash tox

# compile docs
[group('dev')]
docs:
    make docs

# run pre-commit hook
[group('commit')]
pre-commit: lint docs

#
#  Merge
# --------
#
# just pre-merge
# just gh-pr
#

# run pre-merge
[group('merge')]
pre-merge: lint test docs

# create GitHub pull request
[group('merge')]
gh-pr *title:
    # ensure clean state
    git diff --exit-code
    git diff --cached --exit-code
    git ls-files --other --exclude-standard --directory
    git push
    # create pr
    gh pr create -d -t "{{ if title == "" { gh-title } else { title } }}"

#
#  Release
# ---------
#
# just pre-merge
# just bump
# just changelog
# ...proofread changelog...
#
# just pre-merge
# ...commit...
#
# just gh-pr
# ...merge...
#
# just gh-release
# just gh-meta
# just pypi-publish
#

# bump project version
[group('release')]
bump:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run bump-my-version show-bump
    printf 'Choose version part: '
    read PART
    uv run bump-my-version bump -- "$PART"
    uv lock
# collect changelog entries
[group('release')]
changelog:
    uv run towncrier build --yes --version "{{version}}"
    sed -e's/^### \(.*\)$/***\1***/; s/\([a-z]\)\*\*\*$/\1***/' -i '' CHANGELOG.md

# create GitHub release
[group('release')]
gh-release:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{git-head}}" != "main" ]; then
        echo "Can release from main branch only"
        exit 1
    fi
    tag="v{{version}}"
    git tag "$tag" HEAD
    git push origin tag "$tag"
    gh release create -d -t "$tag — $(date -Idate)" --generate-notes "$tag"
# publish package on PyPI
[group('release')]
pypi-publish: build
    uv publish

# update GitHub repository metadata from pyproject.toml
[group('release')]
gh-meta:
    gh repo edit -d "$(yq -r .project.description pyproject.toml)"
    gh repo edit --add-topic "$(yq -r '.project.keywords | join(",")' -ojson pyproject.toml)"
