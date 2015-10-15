#!/bin/bash

# This verifies that any push to master or stable does not cause any failing
# tests.

# This hook is called with the following parameters:
#
# $1 -- Name of the remote to which the push is being done
# $2 -- URL to which the push is being done
#
# If pushing without using a named remote those arguments will be equal.
#
# Information about the commits which are being pushed is supplied as lines to
# the standard input in the form:
#
#   <local ref> <local sha1> <remote ref> <remote sha1>

# FIXME: this does not work if you are not in the root directory
# of the repo!

REMOTE="$1"
URL="$2"
ERRORMSG_TESTS="Push to this branch rejected because of failing tests. Please\
 fix any failing tests and try pushing again."
ERRORMSG_MIGRATIONS="Push to this branch rejected because makemigrations\
 reported that there are missing migrations. Please fix this and try pushing\
 again. NOTE: due to how makemigrations works, new migrations will now\
 have been automatically created in your working directory!"

# FIXME this assumes that you are pushing the current branch. If you are not,
# then this will do the wrong thing!
CURRENT_BRANCH="$(git symbolic-ref --short HEAD)"

function manage() {
    ./manage.py $@
    RESULT=$?
}

# creates a git stash with all changes to working tree, if there are actual
# changes
function push_stash() {
    test -z "$(git ls-files --exclude-standard --others)"
    local UNTRACKED=$?
    git diff-index --quiet HEAD
    local MODIFIED=$?
    if [ $UNTRACKED -ne 0 ] || [ $MODIFIED -ne 0 ]; then
        echo "-= Stashing away your current changes =-"
        git stash -u -q --keep-index
        FILES_STASHED=1
    else
        FILES_STASHED=0
    fi
}

# pops the stash again after finishing, if there were changes
function pop_stash() {
    if [ $FILES_STASHED -eq 1 ]; then
        echo "-= Popping previously created stash =-"
        git stash pop -q
    fi
}

if [ "$CURRENT_BRANCH" == "master" ] || [ "$CURRENT_BRANCH" == "stable" ]; then
    echo "-= Running various tests before pushing to this branch. =-"
    push_stash
    # makemigrations -e returns 1 if there are no migrations pending
    echo ""
    echo "-= Running makemigrations to make sure you haven't forgotten any migrations. =-"
    manage makemigrations -e
    if [ $RESULT -ne 1 ]; then
        pop_stash
        echo ""
        echo $ERRORMSG_MIGRATIONS
        exit 1
    fi
    echo ""
    echo "-= Running backend test suite. =-"
    manage test --failfast
    if [ $RESULT -ne 0 ]; then
        pop_stash
        echo ""
        echo $ERRORMSG_TESTS
        exit 1
    fi
    echo ""
    echo "-= Running frontend test suite. =-"
    npm test
    if [ $? -ne 0 ]; then
        pop_stash
        echo ""
        echo $ERRORMSG_TESTS
        exit 1
    fi
    pop_stash
    echo ""
    echo "-= All tests successful! Going through with push =-"
else
    echo "-= The pre-push script is ignored for this branch =-"
fi

exit 0
