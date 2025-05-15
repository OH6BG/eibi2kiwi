"""
Create JSON-formatted kiwiSDR-compatible broadcast schedules of DX labels
from CSV-formatted broadcast schedules

Copyright (C) 2025 Jari Perkiömäki OH6BG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import csv
import json
import urllib.parse
import re


def percent_encode(station_name, details):
    """
    Encodes the given station_name and details using URL percent encoding.

    Args:
        station_name (str): The name of the station to encode.
        details (str): Additional details to encode.

    Returns:
        dict: A dictionary containing the percent-encoded station_name and details.
    """

    def encode_preserve_case(text):
        # Encode the text and split it into parts
        encoded = (
            urllib.parse.quote(text, safe=" ")
            .replace("%20", " ")
            .replace("%3A", ":")
            .replace("%3C", "<")
            .replace("%3E", ">")
            .replace("%2C", ",")
            .replace("%28", "(")
            .replace("%29", ")")
            .replace("%26", "&")
        )
        # Convert only the percent-encoded parts to lowercase
        return re.sub(r"%[0-9A-Fa-f]{2}", lambda match: match.group(0).lower(), encoded)

    encoded_station_name = encode_preserve_case(station_name)
    encoded_details = encode_preserve_case(details)

    return {
        "encoded_station_name": encoded_station_name,
        "encoded_details": encoded_details,
    }


def day_schedule_to_int(schedule: str) -> int:
    """
    Converts a day-of-week schedule string (e.g., "MTWTFSS") into its integer value.

    Args:
        schedule (str): A 7-character string representing the days of the week.
                        'M' for Monday, 'T' for Tuesday, 'W' for Wednesday,
                        'T' for Thursday, 'F' for Friday, 'S' for Saturday,
                        and 'S' for Sunday. Use '_' for days that are not active.

    Returns:
        int: The integer representation of the schedule.
    """

    # Build the binary representation of the schedule
    binary_representation = "".join(
        "1" if schedule[i] != "_" else "0" for i in range(len(schedule))
    )

    # Convert the binary string to an integer
    return int(binary_representation, 2)


def csv_to_json(input_file, output_file):
    """
    Converts CSV data from a file to a JSON structure and writes it to a file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output JSON file.
    """
    result = []

    # Read the CSV file
    with open(input_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        next(reader, None)  # Skip the header row
        for row in reader:
            if row:  # Skip empty rows
                frequency = round(float(row[0]), 2)
                band = row[1].strip('"')
                station_name = row[2].strip('"')
                details = row[3].strip('"')
                nd = percent_encode(station_name, details)
                metadata = {"T3": 1}  # Add "T3" by default
                if row[10].strip():  # Check if b0 value exists
                    metadata["b0"] = int(row[10].replace("'", "").strip())
                if not row[10].strip() and row[11].strip():
                    metadata["b0"] = 0
                if row[11].strip():  # Check if e0 value exists
                    metadata["e0"] = int(row[11].replace("'", "").strip())
                if not row[11].strip() and row[10].strip():
                    metadata["e0"] = 0
                if row[9].strip():  # Check if d0 value exists
                    metadata["d0"] = day_schedule_to_int(row[9])

                # Append to result
                result.append(
                    [
                        frequency,
                        band,
                        nd["encoded_station_name"],
                        nd["encoded_details"],
                        metadata,
                    ]
                )

    # Write each JSON entry on its own row
    with open(output_file, "w", encoding="utf-8", newline="\n") as jsonfile:
        jsonfile.write('{"EiBi A25 OH6BG":[\n')  # Start the JSON object
        for i, entry in enumerate(result):
            json.dump(entry, jsonfile, ensure_ascii=True, separators=(",", ":"))
            if i < len(result) - 1:  # Add a comma after each entry except the last
                jsonfile.write(",\n")
        jsonfile.write("\n]}\n")  # Close the JSON object


# File paths
input_csv_file = "kiwi.csv"
output_json_file = "kiwi.json"

# Convert CSV to JSON and write to file
csv_to_json(input_csv_file, output_json_file)

print(f"Done, EiBi Kiwi CSV file converted to JSON: '{output_json_file}'.")
