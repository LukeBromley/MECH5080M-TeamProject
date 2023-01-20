import csv

with open('Backend/Approach/log.csv') as csvfile:
    rawdata = csv.reader(csvfile)
    data = list(rawdata)

current_tick = data[0][0]
tick_data = []
for line in data:
    if line[0] == current_tick:
        tick_data.append(line[1:])
    else:
        print("\n\nTick: " + str(current_tick))
        for entry in tick_data:
            print("Car " + str(entry[0]) + " ->  x:" +
                  str(entry[1]) + " y:" + str(entry[2]))
        current_tick = line[0]
        tick_data = []
        tick_data.append(line[1:])
