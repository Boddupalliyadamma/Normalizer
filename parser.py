#import csv

import csv


def parse_csv(csv_file_location: str) -> tuple[list[str], list[tuple]]:
    columHead = []
    data = []

    try:
        with open(csv_file_location, 'r') as file:
            csvRead = csv.reader(file)
            columHead = next(csvRead)  # Read the column headers
            for row in csvRead:
                data.append(tuple(row))  # Read the data and convert each row to a tuple
    except FileNotFoundError:
        print(f"Error: The file {csv_file_location} was not found.")
    except csv.Error as e:
        print(f"Error: An error occurred while reading the CSV file: {e}")

    return columHead, data