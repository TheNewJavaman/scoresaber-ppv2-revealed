import json


def normalize(a, min, max):
    normalized = list(map(lambda x: (x - min) / (max - min), a))


# Load data dump
with open("training_data.json") as f:
    data_dump = json.loads(f.read())

# Set up vast arrays of normalizations
normalizations = {
    "bpm": [],
    "jump_speed": [],
    "jump_offset": [],
    "note_count": [],
    "note_time": [],
    "note_line_index": [],
    "note_line_layer": [],
    "note_type": [],
    "note_cut_direction": [],
    "event_count": [],
    "event_time": [],
    "event_type": [],
    "event_value": [],
    "obstacle_count": [],
    "obstacle_time": [],
    "obstacle_line_index": [],
    "obstacle_type": [],
    "obstacle_duration": [],
    "obstacle_width": [],
    "pp": []
}

min_max_keys = {
    "bpm": (0, 500),
    "jump_speed": (0, 50),
    "jump_offset": (-3, 3),
    "note_count": (0, 5000),
    "note_time": (),
    "note_line_index": (),
    "note_line_layer": (),
    "note_type": (),
    "note_cut_direction": (),
    "event_count": (0, 35000),
    "event_time": (),
    "event_type": (),
    "event_value": (),
    "obstacle_count": (0, 2000),
    "obstacle_time": (),
    "obstacle_line_index": (),
    "obstacle_type": (),
    "obstacle_duration": (),
    "obstacle_width": (),
    "pp": ()
}

# Add in raw data; empty padding will be added later
for mapping in data_dump:
    normalizations["bpm"].append(mapping["input"]["bpm"])
    normalizations["jump_speed"].append(mapping["input"]["jump_speed"])
    normalizations["jump_offset"].append(mapping["input"]["jump_offset"])
    normalizations["note_count"].append(mapping["input"]["note_count"])
    normalizations["event_count"].append(mapping["input"]["event_count"])
    normalizations["obstacle_count"].append(
        mapping["input"]["obstacle_count"])

    for note in mapping["input"]["notes"]:
        normalizations["note_time"].append(note["_time"])
        normalizations["note_line_index"].append(note["_lineIndex"])
        normalizations["note_line_layer"].append(note["_lineLayer"])
        normalizations["note_type"].append(note["_type"])
        normalizations["note_cut_direction"].append(note["_cutDirection"])

    for event in mapping["input"]["events"]:
        normalizations["event_time"].append(event["_time"])
        normalizations["event_type"].append(event["_type"])
        normalizations["event_value"].append(event["_value"])

    for obstacle in mapping["input"]["obstacles"]:
        normalizations["obstacle_time"].append(obstacle["_time"])
        normalizations["obstacle_line_index"].append(obstacle["_lineIndex"])
        normalizations["obstacle_width"].append(obstacle["_width"])
        normalizations["obstacle_type"].append(obstacle["_type"])
        normalizations["obstacle_duration"].append(obstacle["_duration"])

    normalizations["pp"].append(mapping["output"]["pp"])

# Apply normalization to each array
for key in normalizations:
    normalizations[key] = keras.utils.normalize(
        np.array(normalizations[key])).tolist()[0]

# Export as JSON file
with open("normalized_data.json", "w") as f:
    f.write(json.dumps(normalizations))

'''
empty_object = [None] * 5
inputs = []
y = []

# Convert keyed maps to anonymous arrays
for mapping in data_dump:
    notes = [[n[k] for k in n] for n in mapping["input"]["notes"]]
    events = [[n[k] for k in n] for n in mapping["input"]["events"]]
    obstacles = [[n[k] for k in n] for n in mapping["input"]["obstacles"]]
    inputs.append([
        [
            [
                mapping["input"]["bpm"],
                mapping["input"]["jump_speed"],
                mapping["input"]["jump_offset"],
                None,
                None
            ],
            [
                mapping["input"]["note_count"],
                mapping["input"]["event_count"],
                mapping["input"]["obstacle_count"],
                None,
                None
            ]
        ] + [empty_object] * 4998,
        notes + [empty_object] * (5000 - len(notes)),
        events + [empty_object] * (5000 - len(events)),
        obstacles + [empty_object] * (5000 - len(obstacles)),
    ])

X = np.array(inputs)
print(X.shape)
'''
