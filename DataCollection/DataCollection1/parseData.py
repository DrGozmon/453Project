import sys
from sys import argv

if (len(sys.argv) < 5):
    print("Please run the program with the following:")
    print("python3 parseData.py <input_filename> <values_filename> <dates_filename> <time_filename>")
    sys.exit()

script, inputFile, filename1, filename2, filename3 = argv

values_filename = open(filename1, 'w')
dates_filename = open(filename2, 'w')
time_filename = open(filename3, 'w')


with open(inputFile, 'r') as f:
    for line in f:
        value, dateTime = line.split(',')
        date, time = dateTime.split(' ')
        values_filename.write(value)
        values_filename.write('\n')
        dates_filename.write(date)
        dates_filename.write('\n')
        time_filename.write(time)

values_filename.close()
dates_filename.close()
time_filename.close()


