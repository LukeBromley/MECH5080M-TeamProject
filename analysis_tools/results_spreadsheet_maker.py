import openpyxl

# write headers to first row
headers = ['Run Type', 'Junction', 'CPM', 'Delay Mean Average', 'Delay Standard Deviation', 'Delay Maximum',
           'Delay Minimum', 'Delay Number Of Cars', 'Backup Mean Average', 'Backup Standard Deviation', 'Backup Maximum',
           'Backup Time', 'Kinetic Energy Waste Average', 'Kinetic Energy Waste Standard Deviation',
           'Kinetic Energy Waste Maximum', 'Kinetic Energy Waste Minimum']
def main(all_results, wb_name):
    # create a new workbook
    wb = openpyxl.Workbook()
    # select the active worksheet
    ws = wb.active
    csv, paths = get_data(all_results)
    write_spreadsheet(ws, headers, paths)
    add_data(ws, csv)
    ws.freeze_panes = 'A3'
    # save the workbook
    wb.save(wb_name)
    wb.close()
def write_spreadsheet(ws, headers, paths):
    headerTitles = []
    subheaders = []
    splitters = []
    for x, header in enumerate(headers):
        headerTitles.append(header)
        if "Backup" in header:
            for i, path in enumerate(paths):
                subheaders.append("Node " + str(path))
                if i != 0:
                    headerTitles.append("")
            splitters.append(x)
        else:
            subheaders.append("")
    ws.append(headerTitles)
    ws.append(subheaders)
    for j in range(len(splitters)):
        column = splitters[j] + j*(len(paths)-1)
        ws.merge_cells(start_row=1, start_column=column+1, end_row=1, end_column=column+len(paths))

def get_data(all_results):
    paths = []
    data_list = []
    print("Getting from file...")
    for i,result in enumerate(all_results):
        print(str(i) + "/" + str(len(all_results)) + "\n")
        data = get_entry(result)
        data_list.append(data)
        for path in data[1]:
            if path not in paths:
                paths.append(path)
    paths.sort()
    merge_seeds = []
    print("Extracting...")
    for t, dataline in enumerate(data_list):
        print(str(t) + "/" + str(len(data_list)) + "\n")
        uid = dataline[0]
        path_index = dataline[1]
        entry = dataline[2]
        matching = False
        for line in merge_seeds:
            if uid == line[0]:
                matching = True
                for i in range(3, 8):
                    line[2][i].append(entry[i][0])
                for j in range(8,12):
                    for k in path_index:
                        pos = paths.index(k)
                        line[2][j][pos].append(entry[j][path_index.index(k)][0])
                for l in range(12,15):
                    line[2][l].append(entry[l][0])
        if not matching:
            for i in range(8,12):
                buffer = [[""]]*len(paths)
                for p, path in enumerate(path_index):
                    buffer[paths.index(path)] = dataline[2][i][p]
                dataline[2][i] = buffer
            merge_seeds.append(dataline)
    merge_seeds.sort(key=lambda x: x[2][2])
    return merge_seeds, paths

def get_entry(result):
    entry = []
    paths = []
    run_type = (result["RunType"])
    junction = (result["Junction"])[:-5]
    cpm = int(result["RunUID"].split("_")[-1][:-3])
    entry += [run_type,junction,cpm]
    for path in list(result["Backup Mean Average"].keys()):
        paths.append(int(path))
    dma = (result["Delay Mean Average"])
    dsd = (result["Delay Standard Deviation"])
    dmx = (result["Delay Maximum"])
    dmi = (result["Delay Minimum"])
    dnc = (result["Delay Number Of Cars"])
    entry += [[dma], [dsd], [dmx], [dmi], [dnc]]
    bma = []
    bsd = []
    bmx = []
    bti = []
    for path in paths:
        bma.append([result["Backup Mean Average"][str(path)]])
        bsd.append([result["Backup Standard Deviation"][str(path)]])
        bmx.append([result["Backup Maximum"][str(path)]])
        bti.append([result["Backup Time"][str(path)]])
    entry += [bma,bsd,bmx,bti]
    kwa = (result["Kinetic Energy Waste Average"])
    kwd = (result["Kinetic Energy Waste Standard Deviation"])
    kwm = (result["Kinetic Energy Waste Maximum"])
    kwt = (result["Kinetic Energy Waste Time"])
    entry += [[kwa], [kwd], [kwm], [kwt]]
    uid = str(run_type)+str(junction)+str(cpm)
    data = [uid, paths, entry]
    return data


def add_data(ws, csv):
    print("Writing...")
    for t, line in enumerate(csv):
        print(str(t) + "/" + str(len(csv)) + "\n")
        to_write = []
        for data in line[2]:
            if type(data) == list:
                if type(data[0]) == list:
                    for group in data:
                        if group == [""]:
                            to_write.append("")
                        else:
                            to_write.append((sum(group)/len(group)))
                else:
                    to_write.append((sum(data)/len(data)))
            else:
                to_write.append(data)
        ws.append(to_write)