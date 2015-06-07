git_path=/home/git/
project=$1
project_path=${git_path}${project}.git

if [ $UID -ne 0 ]; then
	echo "Superuser privileges are required to run this script."
	exit 1
fi

function git_init_bare(){
	if [ -e "$1" ]; then
		echo "project \"$project\" already exist."
		exit 1
	fi
	mkdir $1 && cd $1
	git --bare init
	chown -R git ./
}

if [ -z "$project" ]; then
	echo "you need enter project name."
	exit 1
else
	git_init_bare $project_path
	echo "create a new bare repository in $project_path."
fi
