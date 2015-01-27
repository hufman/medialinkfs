#!/bin/sh
dir=`dirname $0`
oldpwd="$PWD"
failed=0
cd "$dir"

[ -e tests.log ] && rm tests.log
for i in tests/*.py; do
	testname=`basename $i .py`
	echo "$testname" | grep "^_" > /dev/null && continue
	echo "$testname" | grep "id3" > /dev/null && continue
	echo "$testname" | grep "freebase" > /dev/null && continue
	echo "Running tests in $testname"
	python3 -m unittest tests.$testname || failed=1
	echo
done
cd "$oldpwd"
[ $failed -eq 0 ] && echo "All tests pass" || echo "FAILURES DETECTED"
return $failed
