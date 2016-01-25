DIR=`pwd`
Project='h'
CSCOPE_FILE=cscope.files

function show_help(){
	echo "Usage:  [options] file..."
	echo "Options:"
	echo -e "  -h             help"
	echo -e "  -i <dir>       choose directory"
	echo -e "  -a             android"
	echo -e "  -p             python"
}

function create_index(){
	rm -f cscope.*
	case $Project in 
	h)
		show_help
		exit 0
		;;
	a)
		echo "Project: Android"
		find $DIR -name '*.aidl' -o -name '*.cc' -o -name '*.h' -o -name '*.c' -o -name '*.cpp' -o -name '*.java' -o -name '*.mk' > $CSCOPE_FILE
		;;
	p)
		echo "Project: Python"
		find $DIR -name '*.py' > $CSCOPE_FILE
		;;
	esac
	cscope -bq -i $CSCOPE_FILE
}

while getopts "h?i:ap" opt; do
	case $opt in
	h|\?)
		show_help
		exit 0
		;;
	i)
		DIR=$OPTARG
		if [ -d "$DIR" ]; then
			echo "Directory: $DIR"
		else
			echo "directory not exist!"	
			exit 0
		fi
		;;
	*)
		Project=$opt
		;;
	esac
done

create_index
