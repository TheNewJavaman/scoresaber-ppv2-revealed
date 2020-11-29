# scoresaber-ppv2-revealed

Use machine learning to reverse engineer ScoreSaber's PP algorithm

All of this code is available on [Github](https://github.com/TheNewJavaman/scoresaber-ppv2-revealed)

## 0. Understand map data

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

Once again, pretty self-explanatory. All of these keys are important, but I won't go into too much detail on any specifics. This file directs us to another, `ExpertPlus.dat`. Another JSON-formatted file, this data dump contains all of the mapping information.

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

## 1. Reverse engineer ScoreSaber's new API

It's nice to use a well-formatted API. The original ScoreSaber worked well enough, but thanks to the efforts of Umbranox and team, we have a fresh API to use instead. Using Google Chrome's built-in Network panel under Devtools, I was able to find a few useful endpoints that aren't publicly documented. There are far more available that I have not listed below.

| Key | Description |
| - | - |
| `https://new.scoresaber.com/api` | Base API URL |
| `/players/{page}` | List of top players |
| `/player/{id}/full` | Individual player stats |
| `/player/{id}/scores/top/{page}` | Tops scores for profile |
| `/user/{id}/refresh` | Checks for changes in player stats; weird that it's `/user`, right? |

The issue is that the new ScoreSaber system has not been updated to support leaderboards, so we're out of luck for half the functionality. In that case, we'll have to rely on webscraping pre-rendered HTML pages from the old API. I'm not sure how else to do this -- maybe I can use WireShark to figure out a direct way to access the API by MitM'ing the Beat Saber client? The issue with that method is that it would require debug SSL keys, which are often unavailable in production builds; I'm guessing that Beat Saber doesn't store that type of data.

So, part of the `get_map_data.py` script checks against the old API to see if a certain map is ranked. Except, that's what I would have done if BaliBalo's `/ranked` tool hadn't existed. Using `scoresaber.balibalo.xyz/ranked`, the script loads an aggregate data object of every ranked map. Balo's project is open source on [Github](https://github.com/BaliBalo/ScoreSaber); you should check it out, there are a few useful tools.

## 2. Create data representation

Let's design a data object to use for machine learning. We shouldn't over-simplify nor create an object that's too complex. We want the AI to do its job without too much pruning. There's still the option to just feed the AI the raw file -- but where's the fun in that?

It's important to keep in mind that neural networks are statically designed. Consequently, lists such as the list of notes will have to fit into a fixed array within Tensorflow/Keras; this means that there will be a certain max number of notes/events/obstacles. We can keep that limit high, but it'll increase training time and possibly affect accuracy.

Object format:
```json
{
    "input": {
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
        "pp": 0
    }
}
```

Next up: a script to convert song format to AI format. Check `get_map_data.py` for the full code, but here's a quick overview:
1. Find Beat Saber game directory
2. Get all custom songs
3. Reader metadata in `info.dat`
4. Find all difficulty maps for each song
5. For each ranked map, gather a representative data object
6. Export data objects to `training_data.json`

I didn't include `training_data.json` in this repository because each version is unique to whoever generated it. Additionally, my version of the file is over 181MB in size. Anyone can train the neural network based off of their own game directory.

Let's just hope that the machine learning model can draw proper correlations between the available inputs.

## 3. Create neural network

First up is creating a set of fixed dimensions for the input, hidden, and output layers. The following diagram shows the easiest way to fit in all of the required information; its only downside is the sheer size of the set -- thousands of layers? Insane! It shouldn't work!

```python
empty_object = [  # Dimensions: (5)
    None,
    None,
    None,
    None,
    None
]

structure = [  # Dimensions: (4, 5000, 5)
    [  # Metadata
        [  # Speed object
            "bpm",
            "jump_speed",
            "jump_offset",
            None,
            None,
        ],
        [  # Count object
            "note_count",
            "event_count",
            "obstacle_count",
            None,
            None
        ],
        ...  # Empty objects
    ],
    [  # Notes
        [  # Note object
            "_time",
            "_lineIndex",
            "_lineLayer",
            "_type",
            "_cutDirection"
        ],
        ...  # Note objects followed by empty objects
    ],
    [  # Events
        [  # Event object
            "_time",
            "_type",
            "_value",
            None,
            None
        ],
        ...  # Event objects followed by empty objects
    ],
    [  # Obstacles
        [  # Obstacles object
            "_time",
            "_lineIndex",
            "_type",
            "_duration",
            "_width"
        ],
        ...  # Obstacle objects followed by empty objects
    ]
]
```

Now we have to normalize the available data. This step will allow the neural network to appropriately use any "wild" information we provide. Doing so will adapt all values to a 0 - 1 scale. 
