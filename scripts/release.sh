#!/bin/bash

set -euo pipefail
set -x

REMOTE="ghx"

if [ -z "${GOLLYX_MAPS_HOME}" ]; then
	echo 'You must set the $GOLLYX_MAPS_HOME environment variable to proceed.'
	exit 1
fi

POSITIONAL=

if [[ $# != 2 ]]; then
    echo "Given a source (pre-release) branch and a destination (release) branch,"
	echo "this script does the following:"
	echo " - create a git tag"
	echo " - reset head of destination branch to head of source branch"
	echo " - push result to git repo"
    echo
    echo "Usage: $(basename $0) source_branch dest_branch"
    echo "Example: $(basename $0) release/v1.0 mainx"
    exit 1
fi

if ! git diff-index --quiet HEAD --; then
    echo "You have uncommitted files in your Git repository. Please commit or stash them."
    exit 1
fi

export PROMOTE_FROM_BRANCH=$1 PROMOTE_DEST_BRANCH=$2

if [[ "$(git log ${REMOTE}/${PROMOTE_FROM_BRANCH}..HEAD)" ]]; then
    echo "You have unpushed changes on your promote from branch ${PROMOTE_FROM_BRANCH}! Aborting."
    exit 1
fi

RELEASE_TAG=$(date -u +"%Y-%m-%d-%H-%M-%S")-${PROMOTE_DEST_BRANCH}.release

if [[ "$(git --no-pager log --graph --abbrev-commit --pretty=oneline --no-merges -- $PROMOTE_DEST_BRANCH ^$PROMOTE_FROM_BRANCH)" != "" ]]; then
    echo "Warning: The following commits are present on $PROMOTE_DEST_BRANCH but not on $PROMOTE_FROM_BRANCH"
    git --no-pager log --graph --abbrev-commit --pretty=oneline --no-merges $PROMOTE_DEST_BRANCH ^$PROMOTE_FROM_BRANCH
    echo -e "\nYou must transfer them, or overwrite and discard them, from branch $PROMOTE_DEST_BRANCH."
    exit 1
fi

if ! git --no-pager diff --ignore-submodules=untracked --exit-code; then
    echo "Working tree contains changes to tracked files. Please commit or discard your changes and try again."
    exit 1
fi

git fetch --all
git -c advice.detachedHead=false checkout ${REMOTE}/$PROMOTE_FROM_BRANCH
git checkout -B $PROMOTE_DEST_BRANCH
git tag $RELEASE_TAG
git push --force $REMOTE $PROMOTE_DEST_BRANCH
git push --tags $REMOTE
