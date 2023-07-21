"""
    Create kiwiSDR-compatible broadcast schedules with DX labels
    from EiBi CSV broadcast schedules in Python

    Copyright (C) 2023 Jari Perkiömäki OH6BG

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

FILEIN = "sked-a23.csv"  # INPUT: Eibi CSV file
FILEOUT = "kiwi.csv"  # OUTPUT: File to import into kiwiSDR

outrow, DOW = [], ""
days = {
    "Mo": "1000000",
    "Tu": "0100000",
    "We": "0010000",
    "Th": "0001000",
    "Fr": "0000100",
    "Sa": "0000010",
    "Su": "0000001",
}


def expand_weekday_range(weekday_range):
    """
    Expand a weekday range of e.g. "Mo-Th" to "Mo,Tu,We,Th"
    Also "Sa-Tu" will be "Sa,Su,Mo,Tu"
    """
    weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    start, end = weekday_range.split("-")
    start_index = weekdays.index(start)
    end_index = weekdays.index(end)
    if start_index <= end_index:
        result = weekdays[start_index : end_index + 1]
    else:
        result = weekdays[start_index:] + weekdays[: end_index + 1]
    return ",".join(result)


def weekdays_to_binstrings(weekdays, days_dict):
    """
    Convert weekday abbreviations, e.g. "Mo,Tu,We,Th", to weekday bin strings
    Returns a list of weekday bin strings
    """
    result = []
    for day in weekdays.split(","):
        result.append(days_dict[day])
    return result


def weekdaynumbers_to_binstrings(numbers_string, days_dict):
    """
    Convert weekday daynumbers, e.g. "1345", to a list of weekday abbreviations ["Mo","We","Th","Fr"]
    Then run "weekdays_to_binstrings" function to get weekday bin strings
    Returns a list of weekday bin strings
    """
    daylist = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    weekdays_list = []
    for number in numbers_string:
        index = int(number) - 1
        weekdays_list.append(daylist[index])
    return weekdays_to_binstrings(",".join(weekdays_list), days_dict)


def create_weekly_binstring(bin_strings):
    """
    Create a combined weekly bin string from a list of weekday bin strings
    Also one argument is OK
    """
    result = ""
    for bits in zip(*bin_strings):
        if any(bit == "1" for bit in bits):
            result += "1"
        else:
            result += "0"
    return result


def binstring_to_decimal(bin_string):
    """
    Convert a bin string to decimal value for DOW. Not used in CSV.

    Check that all values in bin_string are either 0 or 1;
    otherwise just return the bin_string
    """
    if all(c in "01" for c in bin_string):
        decimal = 0
        for i in range(len(bin_string)):
            decimal += int(bin_string[i]) * pow(2, len(bin_string) - i - 1)
        return decimal

    return bin_string


def binstring_to_dowstring(bin_string):
    """
    Convert a bin string to a "MTWTFSS" formatted string. Used in CSV.
    """
    days = ["M", "T", "W", "T", "F", "S", "S"]
    day_of_week_string = ""
    for i in range(len(bin_string)):
        if bin_string[i] == "1":
            day_of_week_string += days[i]
        else:
            day_of_week_string += "_"
    return day_of_week_string


with open(FILEIN, "r") as inf:
    reader = csv.reader(inf, delimiter=";")
    next(reader)  # skip the header line
    for row in reader:
        khz = float(row[0])
        begin, end = row[1].split("-")
        # avoid using "0000" and "2400" directly
        if begin == "0000":
            begin = "0001"
        if end == "2400":
            end = "2359"
        day = row[2]
        if day.isdigit():
            r = weekdaynumbers_to_binstrings(day, days)
            s = create_weekly_binstring(r)
            DOW = binstring_to_dowstring(s)
        elif "," in day or day in days.keys() or day == "SaSu" or day.startswith("1."):
            if day == "SaSu":
                day = "Sa,Su"
            if day.startswith("1."):
                day = day[2:]
            r = weekdays_to_binstrings(day, days)
            s = create_weekly_binstring(r)
            DOW = binstring_to_dowstring(s)
        elif "-" in day:
            r = expand_weekday_range(day)
            r = weekdays_to_binstrings(r, days)
            s = create_weekly_binstring(r)
            DOW = binstring_to_dowstring(s)
        if not DOW:
            DOW = ""
        else:
            DOW = f'"{DOW}"'
        itu = row[3]
        ident = row[4]
        lang = row[5].strip()
        if lang.startswith("-") or not lang:
            type = "T4"
        else:
            type = "T3"
        if not lang:
            lang = ""
        else:
            lang = f"Lang: {lang}"
        target = row[6].strip()
        if not target:
            target = ""
        else:
            target = f"Target: {target}."
        rem = row[7]
        if not rem:
            notes = f"{itu}. {target} {lang}"
        else:
            notes = f"{itu} via {rem}. {target} {lang}"
        outrow.append(
            [
                str(khz),
                f'"QAM"',
                f'"{ident}"',
                f'"{notes.strip()}"',
                "",
                f'"{type}"',
                "",
                "",
                "",
                DOW,
                str(begin),
                str(end),
            ]
        )
        DOW = ""

# sort the output list of lists by the frequency
# which is the first (stringified) element in the lists
# (converted to float for correct sorting)
outrow.sort(key=lambda x: float(x[0]))

with open(FILEOUT, "w", encoding="utf-8") as outf:
    for row in outrow:
        outf.write(";".join(row) + "\n")
