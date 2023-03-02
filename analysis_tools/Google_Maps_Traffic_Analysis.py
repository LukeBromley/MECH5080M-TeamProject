import csv
import requests
import time as Time


class GoogleMapsTrafficAnalysis:
    def __init__(self):
        api_key = input("Please enter your Google Maps API Key: ")
        start_time = self.get_time("Enter UNIX start time (must be future): ", Time.time(), 2524608000)

        while True:
            # 53.810803, -1.556368
            from_latitude = self.get_loc("Enter from latitude: ", -90, 90)
            from_longitude = self.get_loc("Enter from longitude: ", -180, 180)
            # 53.812291, -1.558325
            to_latitude = self.get_loc("Enter to latitude: ", -90, 90)
            to_longitude = self.get_loc("Enter to longitude: ", -180, 180)

            file_name = input("File name of where to save data to (include .csv): ")

            print("Gathering data!!")

            traffic_data = []

            for day in range(7):
                for hour in range(24):
                    for quarter in range(4):
                        time = start_time + day * 86400 + hour * 3600 + quarter * 900

                        url = f'https://maps.googleapis.com/maps/api/directions/json?origin={from_latitude},{from_longitude}&destination={to_latitude},{to_longitude}&departure_time={time}&traffic_model=best_guess&key={api_key}'

                        response = requests.get(url)
                        data = response.json()

                        # The current traffic for the road is stored in the "duration_in_traffic" field
                        duration_in_traffic = data['routes'][0]['legs'][0]['duration_in_traffic']['value']
                        duration = data['routes'][0]['legs'][0]['duration']['value']
                        distance = data['routes'][0]['legs'][0]['distance']['value']
                        print("Day: ", day + 1, "Hour: ", hour, "Quarter: ", quarter * 15, "-", duration_in_traffic, duration)
                        traffic_data.append([day + 1, hour, quarter * 15, duration_in_traffic, duration, distance])

            print("Saving data!!")

            csv_file = open(file_name, 'w')
            csv_writer = csv.writer(csv_file)
            for time in traffic_data:
                csv_writer.writerow(time)
            csv_file.close()

            print("Saved!")

            print("Starting again. Feel free to enter a new location and time!")

    def get_loc(self, prompt, min, max):
        valid_loc = False
        loc_float = None
        while not valid_loc:
            loc_str = input(prompt)
            try:
                loc_float = float(loc_str)
                if min <= loc_float <= max:
                    valid_loc = True
                else:
                    print("Invalid location entered. Try again.")
            except ValueError:
                print("Invalid location entered. Try again.")
        return loc_float

    def get_time(self, prompt, min, max):
        valid_time = False
        time_float = None
        while not valid_time:
            time_str = input(prompt)
            if time_str.isdigit() and "." not in time_str:
                time_float = int(time_str)
                if min <= time_float <= max:
                    valid_time = True
                else:
                    print("Invalid time entered. Try again.")
            else:
                print("Invalid time entered. Try again.")
        return time_float


traffic_analysis = GoogleMapsTrafficAnalysis()

