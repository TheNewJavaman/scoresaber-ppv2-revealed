# scoresaber-ppv2-revealed

Use machine learning to reverse engineer ScoreSaber's PP algorithm

All of this code is available on [Github](https://github.com/TheNewJavaman/scoresaber-ppv2-revealed)

## 0. get map data

Each map in Beat Saber is structured in the following manner. Some mods may allow for customization of a map, thus additional parameters may be included. Here, we will use Overkill mapped by Krydar as an example.

Directory structure:

```
1ef6 (Overkill - Krydar)/
    cover.jpg
    ExpertPlus.dat
    info.dat
    song.egg
```

All of the filenames are self-explanatory. Let's take a look at the `info.dat` file to retrieve meta data. It looks like it's JSON-formatted, which makes life simpler for us!

`info.dat`:
```json
{
    "_version": "2.0.0",
    "_songName": "Overkill",
    "_songSubName": "",
    "_songAuthorName": "RIOT",
    "_levelAuthorName": "Kry",
    "_beatsPerMinute": 174,
    "_songTimeOffset": 0,
    "_shuffle": 0,
    "_shufflePeriod": 0.5,
    "_previewStartTime": 253.72500610351562,
    "_previewDuration": 18,
    "_songFilename": "song.egg",
    "_coverImageFilename": "cover.jpg",
    "_environmentName": "BigMirrorEnvironment",
    "_customData": {
        "_contributors": [],
        "_customEnvironment": "",
        "_customEnvironmentHash": ""
    },
    "_difficultyBeatmapSets": [
        {
        "_beatmapCharacteristicName": "Standard",
        "_difficultyBeatmaps": [
            {
            "_difficulty": "ExpertPlus",
            "_difficultyRank": 9,
            "_beatmapFilename": "ExpertPlus.dat",
            "_noteJumpMovementSpeed": 17,
            "_noteJumpStartBeatOffset": 0,
            "_customData": {
                "_difficultyLabel": "",
                "_editorOffset": 0,
                "_editorOldOffset": 0,
                "_warnings": [],
                "_information": [],
                "_suggestions": [],
                "_requirements": []
            }
            }
        ]
        }
    ]
}
```

Once again, pretty self-explanatory. All of these keys are important, but I won't go into too much detail on any specifics. This file directs us to another, `ExpertPlus.data`. Another JSON-formatted file, this data dump contains all of the mapping information.

`ExpertPlus.dat`:
```json
{
    "_version": "2.0.0",
    "_BPMChanges": [],
    "_events": [...],
    "_notes": [...],
    "_obstacles": [...],
    "_bookmarks": []
}
```

Simple, right? This Overkill example is mapped in version `2.0.0`. In-depth explanations of each data dump can be found on the [BSMG website](https://bsmg.wiki/mapping/map-format.html). Here are the most important keys:

| Key | Description |
| - | - |
| `_version` | Keeps track of the Beat Saber map format |
| `_events` | List of events that occur |
| `_notes` | List of notes in the map |
| `_obstacles` | List of obstacles in the map |

## 1. Create data representation

Let's design a data object to use for machine learning. We shouldn't over-simplify nor create an object that's too complex. We want the AI to do its job without too much pruning. There's still the option to just feed the AI the raw file -- but where's the fun in that?

Object format:
```json
{
    "input": {
        "author": "",
        "bpm": 0,
        "jump_speed": 0,
        "jump_offset": 0,
        "note_count": 0,
        "notes": [],
        "event_count": 0,
        "events": [],
        "obstacle_count": 0,
        "obstacles": []
    },
    "output": {
        "difficulty": 0,
        "pp": 0
    }
}
```

Let's just hope that the machine learning model can draw proper correlations between the available inputs.

Next up: a script to convert song format to AI format.

Within `get_map_data.py`:
```python
import json

def bs2_0_0_to_ai(map_file_string):
    map_data = json.loads(map_file_string)
```

## 2. Reverse engineer ScoreSaber's new API

It's nice to use a well-formatted API. The original ScoreSaber worked well enough, but thanks to the efforts of Umbranox and team, we have a fresh API to use instead. Using Google Chrome's built-in Network panel under Devtools, I was able to find a few useful endpoints that aren't publicly documented. There are far more available that I have not listed below.

| Key | Description |
| - | - |
| `https://new.scoresaber.com/api` | Base API URL |
| `/players/{page}` | List of top players |
| `/player/{id}/full` | Individual player stats |
| `/player/{id}/scores/top/{page}` | Tops scores for profile |