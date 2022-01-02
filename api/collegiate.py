import requests

import os
from dotenv import load_dotenv
from string import punctuation


load_dotenv(".env")
KEY = os.getenv("COLLEGIATE")


def audio_file(sound):
    langage_code = "en"
    country_code = "us"
    audio_format = "mp3"
    filename = sound["audio"]

    if filename[:2] == "gg":
        subdir = "gg"
    elif filename[:3] == "bix":
        subdir = "bix"
    elif filename[0].isnumeric() or filename[0] in punctuation:
        subdir = "number"
    else:
        subdir = filename[0]

    return f"https://media.merriam-webster.com/audio/prons/{langage_code}/{country_code}/{audio_format}/{subdir}/{filename}.{audio_format}"


def word_lookup(json: dict):
    sound_pr = audio_file(json["hwi"]["prs"][0]["sound"])
    error = None
    match json['meta']['section']:
        case 'alpha':
            section_type = 'word'
        case 'biog':
            section_type = 'biography'
        case 'fw&p':
            section_type = 'foreign & phrases'
        case _:
            error = 'Unknown section'
            
    return {
        'error': error,
        'type': section_type,
        'label': json['fl'],
        "definition": json["shortdef"][0],
        "text_pr": json["hwi"]["prs"][0]["mw"],
        "audio_url": sound_pr,
    }


def suggestion_list(json: list):
    return {"type": "suggestion", "suggestion": json}


def collegiate_request(word: str):
    r = requests.get(
        f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={KEY}"
    )


    response = {'error': None, "word": word}

    if r.status_code == 200:
        json = r.json()
        if isinstance(json[0], dict):
            response.update(word_lookup(json[0]))
            return response
        elif isinstance(json[0], str):
            response.update(suggestion_list(json))
            return response
    else:
        response['error'] = f"{r.status_code} HTTP Request failed"
        return response
