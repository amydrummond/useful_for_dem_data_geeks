## 1. Ask for the file
## 2. Determine delimiter and confirm.
##  -- this will require getting all unique characters into a list: list(set(input))
##  -- count numbers of each character
##  -- the largest one should be the delimiter
## 3. confirm the delimiter with user
## 4. Double apostrophes for Vertica upload
## 5. Divide into columns
## 6. Detect the datatype for each column
## 7. Detect length for each column
## 6. Output the list of data types and lengths for confirmation
## 7. Create a CREATE TABLE file for upload
## 8. Create a INSERT INTO VALUES file for upload

### This will not detect '\n' or ' ' as delimiters. \n is too comon as an EOL character, and
### space is far too common in appearing multiple times in a record.

import random
import csv
import os

## Add the filename and path 
upload_file = "FILEPATH-AND-NAME"
## Add the destination table name for the database
table_name = "SCHEMA-AND-TABLENAME"
### If your data has headers, this should be 'Y', if it doesn't, 'N'
header = 'N'
file_object = open(upload_file, 'r')
data = file_object.read()

### This detects a delimiter.  It does so by counting the number of each character in each line except for the 
### first one, then comparing that to the count of the same character in the previous line. In comparing the first
### two lines, the characters that have identical counts are added to a dictionary. In the subsequent lines, if the 
### count for that character does not equal the count in the dictionary, the character is removed from the 
### dictonary.  A character should remain, and it should be the file delimter.


data_lines = data.split("\n")
if len(data_lines)>= 2000:
    test_data = random.sample(data_lines, 2000)
else:
 test_data = data_lines

line_max = {}

for index, line in enumerate(test_data):
	first_line_char_count = {}
	second_line_char_count = {}
	if index != 1:
		line_one = test_data[index-1]
		line_two = test_data[index]
		for letter in line_one:
			letter_count = line_one.count(letter)
			first_line_char_count[letter] = letter_count
		for letter in line_two:
			letter_count = line_two.count(letter)
			second_line_char_count[letter] = letter_count
		if line_max == {}:
			for char_one in first_line_char_count.keys():
				for char_two in second_line_char_count.keys():
					if char_one == char_two:
						if first_line_char_count[char_one] == second_line_char_count[char_two]:
							line_max[char_one] = first_line_char_count[char_one]
		else:
			for char_one in first_line_char_count.keys():
				for char_two in second_line_char_count.keys():
					if char_one == char_two:
						if first_line_char_count[char_one] == second_line_char_count[char_two]:
							if char_one in line_max.keys():
								if line_max[char_one] != first_line_char_count[char_one]:
									line_max.pop(char_one, None)			

max_total = max(line_max.values())
for c, v in line_max.items():
	if v == max_total:
		delim = c



### Now that we have a delimiter, we can break up the data into lists of lists.
div_data = []
if delim == ',':
    with open(upload_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            div_data.append(row)
else:
    for line in data_lines:
        div_data.append(line.split(delim))

### Divide the data into data and header.
	
if header == 'Y':
    header_row = div_data[0]
    div_data = div_data[1:]
if header == 'N':
    header_row = []
    q = 1
    while q <= len(div_data[0]):
        header_row.append("Field_"+str(q))
        q = q+1

### Detect data-type and length.  First: test if contains only numbers and periods.
### If it is, then test to see if the first digit is a 0 -- then it's really a string.
### In the future, this portion should detect dates and times.
### Everything that is not a number (with or without periods) or a date is a string.
### Count the length of each string. Use the largest.


if len(div_data)>= 2000:
    test_data = random.sample(div_data, 2000)
else: 
    test_data = div_data

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

data_type = {}
data_length = {}

for index, field in enumerate(test_data[0]):
    data_length[index] = len(field)
    if is_number(field):
        if is_integer(field):
            if len(field)>= 8:
                data_type[index] = "BIGINT"
            else:
                data_type[index] = "INT"
        else:
            data_type[index] = "FLOAT"
    else:
        data_type[index] = "VARCHAR"

for row in test_data[1:]:
    for index, field in enumerate(row):
        if is_number(field):
            if is_integer(field):
                if len(field)>= 8:
                    f_type = "BIGINT"
                else:
                    f_type = "INT"
            else:
                f_type = "FLOAT"
        else:
            f_type = "VARCHAR"
        if data_type[index] != "VARCHAR":
            if f_type == "VARCHAR":
                data_type[index] == "VARCHAR"
            if data_type[index] == "INT":
                if f_type == "BIGINT":
                    data_type[index] = "BIGINT"
                if f_type == "FLOAT":
                    data_type[index] = "FLOAT"
            if data_type[index] == "BIGINT":
                if f_type == "FLOAT":
                    data_type[index] = "FLOAT"
        f_length = len(field)
        if f_length > data_length[index]:
            data_length[index] = f_length

q_fields = len(div_data[0])
q_rows = len(div_data)

### Replace quotes with double quotes for upload.

for row in div_data:
    for item in row:
        item.replace("'","''")

### Now we create the "CREATE TABLE" script
    
head_row = "CREATE TABLE IF NOT EXISTS "+table_name+" ("
q = 0
text = head_row + "\n"
while q < q_fields:
    if data_type[q]=="VARCHAR":
        line = header_row[q]+" VARCHAR("+str(data_length[q]+1)+"),\n"
    else:
        line = header_row[q]+" "+data_type[q]+",\n"
    text=text+line
    q = q+1

text = text[:-2]
text = text+";\n\n"

### Now we create the "INSERT INTO" script

q = 0
while q < q_rows:
    line ="INSERT INTO "+table_name+ " VALUES("
    for field in div_data[q]:
        line = line + "'"+str(field)+"', "
    line = line[:-2]
    line = line +");\n"
    text = text+line
    q = q+1

text = text+"\n\n-- done"

### And now export the file.
filename = "create_"+table_name+".sql"
with open(filename, 'w') as final_sql:
    final_sql.write(text)

print os.getcwd()
