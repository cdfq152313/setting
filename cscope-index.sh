rm -f cscope.*
find . -name '*.py' > cscope.files
cscope -bq
