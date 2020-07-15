#!/bin/bash
echo "Checking out tools available"
for tool in "pip3" "7z" "unzip" "unrar" "tar"
do
	type $tool > /dev/null 2>&1
	if [[ $? == 1 ]]
	then
		echo "Package providing $tool is missing"
		err=True
	else
		if [[ $tool == 'pip3' ]]; then echo "Installing python requirements"; pip3 install termcolor pyrogram tgcrypto > /dev/null 2>&1; fi
	fi
done

if [[ $err == True ]]
then echo "Requirements are not satisfied. Script cannot be executed successfully"
else echo "Done!"
fi