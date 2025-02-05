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
    sudo port install gh uv
    uv tool install "docsub>=0.8"  # use global b/c docsub depends on importloc
    just sync
    # pre-commit hook
    echo -e "#!/usr/bin/env bash\njust pre-commit" > .git/hooks/pre-commit
    chmod a+x .git/hooks/pre-commit


# synchronize local dev environment
[group('dev')]
sync:
    uv sync --all-groups


# update local dev environment
[group('dev')]
upd:
    uv sync --all-groups --upgrade


# add news item of type
[group('dev')]
news type issue *msg:
    #!/usr/bin/env bash
    set -euo pipefail
    issue="{{ if issue == "-" { gh-issue } else { issue } }}"
    msg="{{ if msg == "" { gh-title } else { msg } }}"
    uv run towncrier create -c "$msg" "$issue.{{type}}.md"


# run linters
[group('dev')]
lint:
    uv run mypy .
    uv run ruff check
    uv run ruff format --check


# build python package
[group('dev')]
build: sync
    make build


# run tests
[group('dev')]
test *toxargs: build
    time docker compose run --rm -it tox \
        {{ if toxargs == "" { "run-parallel" } else { "run" } }} \
        --installpkg="$(find dist -name '*.whl')" {{toxargs}}


# enter testing docker container
[group('dev')]
shell:
    docker compose run --rm -it --entrypoint bash tox


# compile docs
[group('dev')]
docs:
    make docs


#
#  Commit
# --------
#


# run pre-commit hook
[group('commit')]
pre-commit: lint docs


# create GitHub pull request
[group('commit')]
gh-pr *title:
    gh pr create -d -t "{{ if title == "" { gh-title } else { title } }}"


#
#  Release
# ---------
#
# just lint
# just test
# just docs
#
# just gh-pr
#
# just bump
# just changelog
# (proofread changelog)
#
# just docs
# just build
# (merge pull request)
#
# just gh-release
# just pypi-publish
#


# bump project version
[group('release')]
bump:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run bump-my-version show-bump
    printf 'Choose bump path: '
    read BUMP
    uv run bump-my-version bump -- "$BUMP"
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
    git tag "v$tag" HEAD
    gh release create -d -t "$tag — $(date -Idate)" --generate-notes "$tag"


# publish package on PyPI
[group('release')]
pypi-publish: build
    uv publish
