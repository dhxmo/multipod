import json
import logging

# Configure logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
        elif event["Start"] <= current_event["End"] + 1:
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
            event["Duration"] = 3.0
            event["End"] += 3.0

    # Optionally, print or save the merged_data
    # print(json.dumps(merged_data, indent=2))
    with open(mod_json_file_name, "w", encoding="utf-8") as file:
        json.dump(merged_data, file, indent=4)


def combine_mod_jsons(mod_json_1, mod_json_2, combined_json, name_1, name_2):
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

    # Optionally, write the combined and updated data back to a new JSON file
    with open(combined_json, "w") as outfile:
        json.dump(combined_data, outfile, indent=2)
