import json
import os
import re
from urllib.request import urlopen, Request

with urlopen("https://scoresaber.balibalo.xyz/ranked") as f:
    ranked_maps = json.loads(f.read())["list"]

game_dir = "C:/Program Files (x86)/Steam/steamapps/common/Beat Saber/"
custom_songs = game_dir + "Beat Saber_Data/CustomLevels/"
songs = [f.name for f in os.scandir(custom_songs) if f.is_dir()]

ranked_data = []

# For every custom song
for song in songs:
    # Find the BeatSaver id
    beatsaver_id = re.search("(.*?) ", song).group(0).replace(" ", "")
    with open(custom_songs + song + "/info.dat") as f:
        # Load the file metadata
        metadata = json.loads(f.read())
        # Find supported beatmap version
        if metadata["_version"] == "2.0.0":
            # Get two-saber levels
            try:
                standard_beatmaps = [t for t in metadata["_difficultyBeatmapSets"]
                                     if t["_beatmapCharacteristicName"] == "Standard"][0]["_difficultyBeatmaps"]
            except:
                standard_beatmaps = []
            # For each two-saber level
            for difficulty_map in standard_beatmaps:
                difficulty = difficulty_map["_difficulty"]
                # Check if the level is ranked
                for ranked_map in ranked_maps:
                    # If so, create an AI-compatible data dump
                    if ranked_map["beatSaverKey"] == beatsaver_id and ranked_map["diff"] == difficulty:
                        # Load map
                        level_filename = difficulty_map["_beatmapFilename"]
                        with open(custom_songs + song + "/" + level_filename) as f:
                            level = json.loads(f.read())

                        # Construct data object
                        map_data = {
                            "input": {
                                "bpm": metadata["_beatsPerMinute"],
                                "jump_speed": difficulty_map["_noteJumpMovementSpeed"],
                                "jump_offset": difficulty_map["_noteJumpStartBeatOffset"],
                                "note_count": len(level["_notes"]),
                                "notes": level["_notes"],
                                "event_count": len(level["_events"]),
                                "events": level["_events"],
                                "obstacle_count": len(level["_obstacles"]),
                                "obstacles": level["_obstacles"]
                            },
                            "output": {
                                "pp": ranked_map["pp"]
                            }
                        }

                        ranked_data.append(map_data)
                        break

        else:
            print("Version", metadata["_version"],
                  "is unsupported for song", song)

with open("training_data.json", "w") as f:
    f.write(json.dumps(ranked_data))
