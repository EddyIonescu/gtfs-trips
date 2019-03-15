# Returns trip durations of each trip ID provided in a CSV file.
# Intended for backfilling the cost of trips, based on duration (seconds), given only their trip ID

# Note: TTC changes all its trip IDs every board period, and so the given trip IDs
# correspond to any one past GTFS file in the gtfs directory.

import datetime
import json
import os

GTFS_DIR= './GTFS'
TRIPS_PATH = './existing_school_trips.json'
TRIP_ID_KEY = 'Trip ID'
TRIPS_OUTPUT = './backfill_trips.csv'

TRIPS = {}


def get_trips(stop_times_path):
    with open(stop_times_path, 'r') as stop_times:
        trip_start_time = None
        trip_latest_time = None
        prev_trip_id = ''
        for stop_time in stop_times:
            # arrival and departure times are the same for TTC
            (trip_id, arrival_time) = stop_time.split(',')[:2]
            if trip_id == prev_trip_id:
                trip_latest_time = arrival_time
                continue
            if prev_trip_id != '':
                TRIPS[prev_trip_id] = {
                  'start_time': trip_start_time,
                  'end_time': trip_latest_time,
                }
            trip_start_time = arrival_time
            trip_latest_time = arrival_time
            prev_trip_id = trip_id


def get_duration(trip_id):
    start_time = TRIPS[trip_id]['start_time']
    end_time = TRIPS[trip_id]['end_time']
    FMT = '%H:%M:%S'
    tdelta = datetime.datetime.strptime(end_time, FMT) - datetime.datetime.strptime(start_time, FMT)
    return tdelta.seconds


def main():
    gtfs_list = os.listdir(GTFS_DIR)
    for gtfs in gtfs_list:
        print(gtfs)
        if os.path.isdir(os.path.join(GTFS_DIR, gtfs)):
            stop_times_path = os.path.join(GTFS_DIR, gtfs, 'stop_times.txt')
            get_trips(stop_times_path=stop_times_path)
    trip_durations_backfill = []
    with open(TRIPS_PATH, 'r') as trips:
        trips = json.loads(trips.read())
        for trip in trips:
            trip_id = str(trip[TRIP_ID_KEY])
            if trip_id not in TRIPS:
                print(trip_id, 'not in provided GTFS files')
                continue
            trip_durations_backfill.append('{trip_id},{start_time},{end_time},{duration},\n'.format(
                trip_id=trip_id,
                start_time=TRIPS[trip_id]['start_time'],
                end_time=TRIPS[trip_id]['end_time'],
                duration=get_duration(trip_id=trip_id),
            ))
    with open(TRIPS_OUTPUT, 'w') as trips_output:
        trips_output.writelines(trip_durations_backfill)


if __name__ == "__main__":
    main()
