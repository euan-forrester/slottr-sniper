while getopts c: flag
do
    case "${flag}" in
        c) configfile=${OPTARG};;
    esac
done

export ENVIRONMENT=prod

if [ -z ${configfile+x} ]; 
then 
    caffeinate -s ../src/book-pool.py; 
else 
    caffeinate -s ../src/book-pool.py -c "$configfile";
fi
