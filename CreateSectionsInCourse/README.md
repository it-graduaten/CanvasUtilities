# Create sections in a course
This script will create sections in a course if they do not already exist.

After creating (or getting the existing) section, it will enroll the user in the section. Users will be loaded from Excel (.xlsx) files. 
Users will be matched on their r-number (column 'Inlognummer' in the file). If the user does not exist, the script will print an error and skip the user.