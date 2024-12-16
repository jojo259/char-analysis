import os
import tarfile
import requests
import time
from collections import defaultdict
import unicodedata
from bs4 import BeautifulSoup
import re
from langcodes import Language
import config
import json

corpus_base_url = "https://downloads.wortschatz-leipzig.de/corpora/"

os.makedirs("corpora_files", exist_ok=True)
os.makedirs("corpora_files_extracted", exist_ok=True)
os.makedirs("letters", exist_ok=True)
os.makedirs("speakers", exist_ok=True)

languages = config.languages

def attempt_download(language, file_path):
    if os.path.exists(file_path):
        print(f"found tar: {file_path}")
        return file_path

    for size in config.corpus_sizes:
        for year in config.corpus_years:
            for corpus_type in config.corpus_types:
                file_name = f"{language}_{corpus_type}_{year}_{size}.tar.gz"
                download_url = f"{corpus_base_url}{file_name}"
                print(f"attempting to download: {download_url}")

                try:
                    response = requests.get(download_url, stream=True)
                    if response.status_code == 200:
                        with open(file_path, "wb") as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        print(f"downloaded and saved: {file_path}")
                        return file_path
                    else:
                        print(f"file not found: {download_url} (HTTP {response.status_code})")
                except Exception as e:
                    print(f"error downloading {download_url}: {e}")

                time.sleep(1)
    print(f"no available corpus found for {language}.")
    return None


def extract_and_process_corpus(language, sentences_output_file):
    if os.path.exists(sentences_output_file):
        print(f'found sentences file: {sentences_output_file}')
        with open(sentences_output_file, "r", encoding="utf-8") as file:
            sentences = file.read().splitlines()
        return sentences

    save_file_path = f"corpora_files/{language}.tar.gz"
    downloaded_file = attempt_download(language, save_file_path)
    if not downloaded_file:
        raise Exception(f'failed to download file {downloaded_file}')

    extracted_path = os.path.join("corpora_files_extracted", language)
    os.makedirs(extracted_path, exist_ok=True)

    print(f"extracting: {save_file_path}")
    with tarfile.open(save_file_path, "r:gz") as tar:
        tar.extractall(path=extracted_path)

    extracted_dirs = os.listdir(extracted_path)
    if not extracted_dirs:
        print(f"no folders found after extraction for {save_file_path}.")
        return []

    target_folder = os.path.join(extracted_path, extracted_dirs[0])
    sentences_file = None

    for file_name in os.listdir(target_folder):
        if file_name.endswith("-sentences.txt"):
            sentences_file = os.path.join(target_folder, file_name)
            break

    if not sentences_file:
        print(f"no `-sentences` file found in {target_folder}.")
        return []

    print(f"reading sentences from: {sentences_file}")
    sentences = []
    try:
        with open(sentences_file, "r", encoding="utf-8", errors="replace") as file:
            for line in file:
                parts = line.split("\t", maxsplit=1)
                if len(parts) > 1:
                    sentence = parts[1].strip().lower()
                    sentences.append(sentence)
    except Exception as e:
        print(f"failed to read sentences from {sentences_file}: {e}")
        return []

    with open(sentences_output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(sentences))
        print(f"saved sentences to: {sentences_output_file}")

    return sentences


def get_language_letters(code):
    file_path = f"letters/{code}-letters.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("letters", [])
    return False


def build_char_frequency(languages):
    char_frequencies = defaultdict(int)
    lang_char_frequencies = {lang: defaultdict(int) for lang in languages}
    total_chars = {lang: 0 for lang in languages}
    total_char_count = 0

    for language in languages:
        sentences_file = os.path.join("corpora_files_extracted", f"{language}_sentences.txt")
        if not os.path.exists(sentences_file):
            raise Exception(f'missing sentences for {language}')
            continue

    for language in languages:
        sentences_file = os.path.join("corpora_files_extracted", f"{language}_sentences.txt")

        with open(sentences_file, "r", encoding="utf-8") as file:
            for at, line in enumerate(file):
                if (at + 1) % 10_000 == 0:
                   print(f'processed {at + 1} sentences for {language}')
                if at > config.use_sentences_count:
                    break
                for char in remove_format_chars(line):
                    if len(char) == 1 and char.isalpha() and is_latin_character(char):
                        lang_char_frequencies[language][char] += 1
                        char_frequencies[char] += 1
                        total_chars[language] += 1
                        total_char_count += 1

        lang_letters = get_language_letters(language)
        if not lang_letters:
            raise Exception(f'missing letters file for {language}')

        lang_char_frequencies[language] = {
            char: freq / total_chars[language]
            for char, freq in lang_char_frequencies[language].items()
            if char in lang_letters
        }
        print(f'finished {language}, {len(lang_char_frequencies[language])} letters: {" ".join(lang_letters)}')

        #for key, val in lang_char_frequencies[language].items():
        #    print(f'{key}: {(val * 100):.1f}')

    for char, count in char_frequencies.items():
        char_frequencies[char] = char_frequencies[char] / total_char_count

    return lang_char_frequencies, char_frequencies


def remove_format_chars(text):
    return ''.join(ch for ch in text if not unicodedata.category(ch).startswith('Cf'))


def get_available_languages():
    print("fetching available languages from Wortschatz...")
    try:
        response = requests.get("https://wortschatz.uni-leipzig.de/en/download")
        if response.status_code != 200:
            print(f"failed to fetch language list (HTTP {response.status_code}).")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        language_links = soup.find_all("a", href=True, class_="btn btn-default btn-xs btn-modal")
        available_languages = [re.search(r'/download/(\w+)', link['href']).group(1) for link in language_links]
        available_languages = ["Sorbian" if x=="Lower Sorbian" else x for x in available_languages]
        print(available_languages)
        return available_languages
    except Exception as e:
        print(f"error fetching or parsing language list: {e}")
        return []


def is_latin_character(char):
    return (
        (0x0000 <= ord(char) <= 0x007F) or  # Basic Latin
        (0x0080 <= ord(char) <= 0x00FF) or  # Latin-1 Supplement
        (0x0100 <= ord(char) <= 0x017F) or  # Latin Extended-A
        (0x0180 <= ord(char) <= 0x024F)     # Latin Extended-B
    )


def is_latin_script(text, threshold=0.9):
    total_chars = len(text)
    if total_chars == 0:
        return False

    latin_count = sum(
        1 for char in text
        if is_latin_character(char)
    )
    return (latin_count / total_chars) >= threshold

def check_language_script(language, sentences_file):
    if not os.path.exists(sentences_file):
        raise Exception(f'sentences file not found to check language for {language}')

    try:
        with open(sentences_file, "r", encoding="utf-8") as file:
            text_sample = " ".join(file.readlines()[:1000])  # take first 1000 lines for analysis
            return is_latin_script(text_sample)
    except Exception as e:
        print(f"error reading file for {language}: {e}")
        return False


def lang_code_to_name(lang_code):
    try:
        language = Language.get(lang_code)
        return language.display_name()
    except LookupError:
        return f"[unknown language]"


def get_language_speakers(code):
    file_path = os.path.join("speakers", code + ".txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return int(file.read())
    else:
        with open(file_path, "w", encoding="utf-8") as file:
            speakers = fetch_language_speakers(code)
            file.write(str(speakers))
            return speakers


def get_letter_speakers(letter):
    return sum(map(get_language_speakers, get_languages_with_char(letter)))


def fetch_language_speakers(code):
    endpoint = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?speakers WHERE {{
        ?lang wdt:P219 '{code}'.
        ?lang wdt:P1098 ?speakers.
    }}
    ORDER BY DESC(?speakers)
    LIMIT 1
    """
    headers = {"Accept": "application/json", "user-agent": "python-bot"}
    response = requests.get(endpoint, params={"query": query, "format": "json"}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        bindings = data.get("results", {}).get("bindings", [])
        if bindings:
            return int(float(bindings[0]["speakers"]["value"]))
        else:
            return None
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


def get_languages_with_char(char):
    return [
        lang for lang in languages
        if char in lang_char_frequencies[lang]
    ]

available_languages = get_available_languages()
filtered_languages = [lang for lang in languages if lang in available_languages]

if len(filtered_languages) < len(languages):
    skipped_languages = set(languages) - set(filtered_languages)
    print(f"skipping unsupported languages: {', '.join(skipped_languages)}")
languages = filtered_languages

print('languages:')
print(languages)

for language in languages:
    sentences_output_file = os.path.join("corpora_files_extracted", f"{language}_sentences.txt")

    extract_and_process_corpus(language, sentences_output_file)

    if not check_language_script(language, sentences_output_file):
        raise Exception(f'language {language} does not use latin script')

def printAndFileLog(text):
    print(text)
    with open("results_log.txt", "a", encoding="utf-8") as file:
        file.write(text + "\n")

lang_char_frequencies, total_char_frequencies = build_char_frequency(languages)
all_chars = set()
for lang in languages:
    for char in get_language_letters(lang):
        all_chars.add(char)
all_chars = list(all_chars)

all_chars = [char for char in all_chars if len(char) == 1 and total_char_frequencies[char] > 0]

def get_letter_chance(lang, letter):
    freq = lang_char_frequencies[lang][letter]
    set_length = config.assumed_text_length
    return 1 - (1 - freq) ** set_length

chars_pop = {
    char: 0 for char in all_chars if len(get_languages_with_char(char)) <= config.max_languages
}

total_pop = 0
for lang in languages:
    speakers = get_language_speakers(lang)
    total_pop += speakers
    for char in lang_char_frequencies[lang]:
        if char in chars_pop:
            chars_pop[char] += speakers

weighted_total_char_frequencies = {}
for letter, freq in total_char_frequencies.items():
    weighted_total_char_frequencies[letter] = freq * (get_letter_speakers(letter) / total_pop)

lang_mults = {}
for lang in languages:
    lang_mults[lang] = 1

chars_list = {}
for char in chars_pop:
    chars_list[char] = chars_pop[char]

scored_chars = {}
while len(chars_list) > 0:
    for char in chars_list:
        total_freq_weighted = 0
        for lang in get_languages_with_char(char):
            total_freq_weighted += lang_char_frequencies[lang][char] * (get_language_speakers(lang) / get_letter_speakers(char)) * lang_mults[lang]
        chars_list[char] = chars_pop[char] * total_freq_weighted * total_char_frequencies[char]
        chars_list[char] = get_letter_speakers(char) * total_freq_weighted

    all_chars_sorted = sorted(chars_list.items(), key=lambda x: x[1], reverse=True)

    for letter, score in all_chars_sorted:
       print(f'{letter} score {score} pop. {get_letter_speakers(letter)} freq. {total_char_frequencies[letter]:.3%} langs: {", ".join(list(map(lang_code_to_name, get_languages_with_char(letter))))}')

    chosen = all_chars_sorted[0][0]
    chosen_score = all_chars_sorted[0][1]
    print(f'chosen {chosen} with total freq {total_char_frequencies[chosen]} {chosen_score:.0f}: {", ".join(list(map(lang_code_to_name, get_languages_with_char(chosen))))}')
    for lang in get_languages_with_char(chosen):
        chance = 1 - get_letter_chance(lang, chosen)
        if char in chars_pop:
            print(f'deweighting {lang} by mult {chance}: {lang_mults[lang]} to {lang_mults[lang] * chance}')
            lang_mults[lang] *= chance
    scored_chars[chosen] = chosen_score
    del chars_list[chosen]

with open("results_log.txt", "w", encoding="utf-8") as file:
    file.write("")

markdown_table_string = (
    "|Letter|Score|Languages|"
    "\n|------|-----|---------|"
    "\n"
)
anki_csv_string = ""
valid = 0
covered_languages = set()
distinctly_covered_languages = set()
printAndFileLog("results:")
for char, score in scored_chars.items():
    valid += 1
    printAndFileLog(f'{char} score: {score:.0f} langs: {", ".join(list(map(lang_code_to_name, get_languages_with_char(char))))}')
    anki_csv_string += f'{char.upper()};{char};{score:.0f};{", ".join(list(map(lang_code_to_name, get_languages_with_char(char))))}\n'
    markdown_table_string += f'|{char.upper()} {char}|{score:.0f}|{", ".join(list(map(lang_code_to_name, get_languages_with_char(char))))}|\n'
    for lang in get_languages_with_char(char):
        covered_languages.add(lang)
        if len(get_languages_with_char(char)) == 1:
            distinctly_covered_languages.add(lang)

with open("anki_letters.csv", "w", encoding="utf-8") as file:
    file.write(anki_csv_string)

with open("markdown_table.md", "w", encoding="utf-8") as file:
    file.write(markdown_table_string)

printAndFileLog(f'listed {len(scored_chars)} chars out of {len(all_chars)} total chars')
printAndFileLog(f'covered {len(covered_languages)}/{len(languages)} languages: {", ".join(list(map(lang_code_to_name, covered_languages)))}')
printAndFileLog(f'with distinct converage for {len(distinctly_covered_languages)}/{len(languages)} languages: {", ".join(list(map(lang_code_to_name, distinctly_covered_languages)))}')
missed_languages = set(languages) - set(covered_languages)
printAndFileLog(f'missed languages: {", ".join(list(map(lang_code_to_name, missed_languages)))}')
