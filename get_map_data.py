import json
import os
import re
from urllib.request import urlopen, Request

if __name__ == "__main__":
    with urlopen("https://scoresaber.balibalo.xyz/ranked") as f:
        ranked_maps = json.loads(f.read())["list"]

    game_dir = "C:/Program Files (x86)/Steam/steamapps/common/Beat Saber/"
    custom_songs = game_dir + "Beat Saber_Data/CustomLevels/"
    songs = [f.name for f in os.scandir(custom_songs) if f.is_dir()]

    for song in songs:
        id = re.search("(.*?) ", song).group(0).replace(" ", "")
        with open(custom_songs + song + "/info.dat") as f:
            metadata = json.loads(f.read())
            if metadata["_version"] == "2.0.0":
                standard_beatmaps = [t for t in metadata["_difficultyBeatmapSets"]
                                     if t["_beatmapCharacteristicName"] == "Standard"][0]["_difficultyBeatmaps"]
                for difficulty_map in standard_beatmaps:
                    difficulty = difficulty_map["_difficulty"]
                    for map in ranked_maps:
                        if map["beatSaverKey"] == id and map["diff"] == difficulty:
                            uid = map["uid"]

                            req = Request(
                                "http://scoresaber.com/leaderboard/" +
                                str(uid),
                                data=None,
                                headers={
                                    "User-Agent": "PostmanRuntime/7.26.8"
                                }
                            )
                            with urlopen(req) as f:
                                html = f.read()
                            stars = float(re.search(
                                "Star Difficulty: <b>.*?</b>", html.decode()).group(0).replace("Star Difficulty: <b>", "").replace("★</b>", ""))
                            pp = stars * 42.114296  # subject to change with PPv3
                            map_data = {
                                "input": {

                                },
                                "output": {
                                    "stars": stars,
                                    "pp": pp
                                }
                            }
                            break
            else:
                print("Version", metadata["_version"],
                      "is unsupported for song", song)
