import json


class Timestamps(object):
    def __init__(self, combined_json):
        self.combined_json = combined_json

    @staticmethod
    def mod_json_2_specs(json_file_name, mod_json_file_name):
        # Load the JSON file
        with open(json_file_name, "r") as file:
            data = json.load(file)

        # Sort the list based on the Start time
        data.sort(key=lambda x: x["Start"])

        merged_data = []
        current_event = None

        for i, event in enumerate(data):
            if current_event is None:
                # This is the first event, so just add it to the merged_data
                current_event = event
                merged_data.append(current_event)
            elif event["Start"] <= current_event["End"] + 2.0:
                # Merge the events
                current_event["End"] = max(event["End"], current_event["End"])
                current_event["Duration"] += event["Duration"]
            else:
                # Add the current event to the merged_data and move to the next event
                if current_event["Key"] != 0:
                    merged_data.append(current_event)
                current_event = event

        # Add the last event if it hasn't been added yet
        if current_event is not None:
            merged_data.append(current_event)

        # Iterate through merged_data again to apply the new rule
        for event in merged_data:
            if event["Duration"] < 2:
                merged_data.remove(event)

        with open(mod_json_file_name, "w", encoding="utf-8") as file:
            json.dump(merged_data, file, indent=4)

    def combine_mod_jsons(self, mod_json_1, mod_json_2, name_1, name_2):
        # Load JSON data from files
        with open(mod_json_1, "r") as file_a, open(mod_json_2, "r") as file_b:
            data_a = json.load(file_a)
            data_b = json.load(file_b)

        # Function to remove the 'Key' key from a dictionary
        def remove_key_from_dict(d):
            return {k: v for k, v in d.items() if k != "Key"}

        # Apply the function to each dictionary in the list
        filtered_data_a = [remove_key_from_dict(d) for d in data_a]
        filtered_data_b = [remove_key_from_dict(d) for d in data_b]

        # Combine the filtered data from both files
        combined_data = filtered_data_a + filtered_data_b

        # Sort the combined data based on the "Start" time
        combined_data.sort(key=lambda x: x["Start"])

        # Iterate through the sorted data and add the "speaker" key
        for item in combined_data:
            item["Speaker"] = name_1 if item in filtered_data_a else name_2

        filtered_data_list = [
            entry for entry in combined_data if float(entry["Duration"]) >= 2
        ]

        # TODO: Process the list to handle overlapping entries
        # processed_dataList = process_overlapping_entries(filtered_data_list)

        silenced_datalist = add_silence(filtered_data_list)

        silenced_both_filler_datalist = add_both_filler(silenced_datalist)

        filtered_silenced_both_filler_datalist = [
            entry
            for entry in silenced_both_filler_datalist
            if float(entry["Duration"]) >= 2
        ]

        with open(self.combined_json, "w") as file:
            json.dump(filtered_silenced_both_filler_datalist, file, indent=2)


def process_overlapping_entries(entries):
    i = 0
    while i + 1 < len(entries):  # Ensure there's a next entry to compare
        current_entry = entries[i]
        next_entry = entries[i + 1]

        # Check if the current entry ends after the next entry starts
        if current_entry["End"] > next_entry["Start"]:
            # Update the Speaker of the current entry to "Both" and remove the next entry
            current_entry["Speaker"] = "Both"
            del entries[i + 1]
        else:
            i += 1  # Move to the next pair without modifying

    return entries


def add_silence(data):
    # Sort the data by Start time
    sorted_data = sorted(data, key=lambda x: x["Start"])

    # Initialize variables to track the last End time and the current gap
    last_end_time = sorted_data[0]["End"]

    # List to hold the filled-in data
    filled_data = [sorted_data[0]]

    # Iterate through the sorted data starting from the second entry
    for entry in sorted_data[1:]:
        # Check if there's a gap before the current entry
        if entry["Start"] > last_end_time:
            # Calculate the duration of the gap
            gap_duration = entry["Start"] - last_end_time

            # Insert a new entry for the gap
            filled_data.append(
                {
                    "Start": last_end_time,
                    "event": "silent",
                    "End": entry["Start"],
                    "Duration": gap_duration,
                    "Speaker": "Both",
                }
            )

        # Update the last End time
        last_end_time = entry["End"]

        # Append the current entry to the filled data
        filled_data.append(entry)

    return filled_data


def add_both_filler(data):
    # Sort the data by Start time
    data.sort(key=lambda x: x["Start"])

    # Iterate through the sorted data
    for i in range(len(data) - 1):  # Loop until the second-to-last item
        current_entry = data[i]
        next_entry = data[i + 1]

        # Check if the End time of the next entry is less than the End time of the current entry
        # And if the Duration of the next entry is greater than 7.0
        if next_entry["End"] < current_entry["End"] and next_entry["Duration"] > 5.0:
            # Change the Speaker of the next entry to "Both"
            next_entry["Speaker"] = "Both"

    return data
