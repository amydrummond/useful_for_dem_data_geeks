import sys
import os
import codecs

original_directory = raw_input('What directory contains the NGP webform exports in .tsv format? ')
target_directory = raw_input('Where would you like to save the files compatible with VAN bulk upload? ')

os.chdir(original_directory)
allfiles = os.listdir(original_directory)
for filename in allfiles:
	filenamelength = filename.find('.')
	newfile = filename[:filenamelength]
	convertfile = filename
	sillycode = codecs.open(convertfile, "r", encoding = 'utf-16-le')

	contentOfFile = sillycode.read()
	sillycode.close()

	contentOfFile
	firstlineend = contentOfFile.find("\n")
	secondlineend = contentOfFile.find("\n", firstlineend+2)
	firstlines = contentOfFile[:(secondlineend+1)]


	sillycodeTemp = codecs.open("{0}/{1}.txt".format(target_directory, newfile), "w", encoding="latin-1", errors="ignore")
	sillycodeTemp.write(contentOfFile.replace(firstlines,""))

	sillycodeTemp.close()

