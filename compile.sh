#!/bin/sh
echo "************************************************************************"
echo  If this script give errors try to change the default Python version
echo  to Python 2.0 or up, or change the line:
echo  python -O -c "import py_compile;py_compile.compile(\"$i\")"
echo  to:
echo  python[version] -O -c "import py_compile;py_compile.compile(\"$i\")"
echo  in the 'compile.sh' script
echo "************************************************************************"
for i in src/*.py 
do
	echo "Bytecompiling file: $i"
	python -O -c "import py_compile;py_compile.compile(\"$i\")"
done
