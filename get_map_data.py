import json
import os


if __name__ == "__main__":
    game_dir = "C:/Program Files (x86)/Steam/steamapps/common/Beat Saber/"
    custom_songs = game_dir + "Beat Saber_Data/CustomLevels/"
    song_dirs = [f.name for f in os.scandir(custom_songs) if f.is_dir()]
    for song in song_dirs:
        with open(custom_songs + song + "/info.dat") as f:
            metadata = json.loads(f.read())
            if metadata["_version"] == "2.0.0":
                print()
            else:
                print("Version", metadata["_version"],
                      "is unsupported for song", song)
