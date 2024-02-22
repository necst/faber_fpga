#!/bin/bash
echo "Running dataset pre-processing"
echo $1
echo $2
echo $3

if [ "$1" = "-h" -o "$1" = "--help" ] ; then
	echo "Change the matlab executable path according to your system and version"
    echo "First parameter CT path" 
    echo "Second parameter PET path" 
    echo "Third parameter Result path"
    exit 0
fi

if [ $# -lt 3 ]; then
    echo "No enough arguments provided"
    exit 1
fi

/Applications/MATLAB_R2020b.app/bin/matlab -nodesktop -nosplash -r "CT_path = '$1'; PET_path = '$2'; PET_Preprocessed = '$3'; Preprocessing"

