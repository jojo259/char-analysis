# European language letter analyser

## Goal

Distinguish European Latin-script languages by identifying letters that are exclusive to a portion of the alphabets.

## Solution

Create a list of letters to learn to recognise, ranked by their distinguishing power when learned sequentially.

## Method

- Retrieve a corpus for each language and a list of letters for each language's alphabet
- Filter out letters that appear in too many languages' alphabets to memorise
- Iteratively repeat this process:
  - Count letter frequency for each language (for only letters that are actually part of a language's alphabet)
  - Score and rank letters multiplicatively by:
    - Their frequency in each language they are part of, weighted by number of speakers
    - The summed number of speakers for the languages they are part of
  - Take the top-ranked letter, append it to a list, and remove it from the pool of letters under consideration
  - Deweight each language that the letter is part of
  - Repeat until all letters have been appended to the ranked list
- Create a CSV for Anki for memorisation

## Implementation

Data is downloaded and cached as files.

Language alphabets are included in-repo - to update them, manually edit the files in the `letters` folder or regenerate them by installing modules from `requirements_alphabet.txt` and running `alphabets.py` (requires ChatGPT API access).

Language speaker counts are included in-repo - to regenerate, delete the `speakers` folder.

ChatGPT was used to write/edit part of the code.

## Parameters

### General

- `languages` - list of Latin-script languages to analyse

### Analysis

- `max_languages`: `4` - the maximum number of languages that a letter can be part of for it to be considered useful (because the user will be memorising letter to languages mappings)
- `use_sentences_count`: `100,000` - the number of corpus sentences to use for letter frequency counting
- `assumed_text_length`: `40` - assumed text length for calculating the chance of a given letter appearing in a piece of text

### Corpus

- `corpus_types`: `wikipedia` - source for corpus
- `corpus_sizes`: `100k, 10k` - size in bytes for corpora to download
- `corpus_years`: `2024 to 2000` - years to check for corpora

### Data sources

- Corpora: The Leipzig Corpora Collection © 2024 Universität Leipzig / Sächsische Akademie der Wissenschaften / InfAI
- Language speaker count: Wikidata
- Language alphabets: Wikipedia pages on language alphabets, orthographies, or their general language pages, processed with ChatGPT-4o mini

## Results (default parameters)

Covers 60 letters out of 104 total for 41 languages.

Languages covered with at least 1 letter (35/41): Azerbaijani, Galician, Italian, Hungarian, Western Frisian, Catalan, Polish, Corsican, Northern Sami, Faroese, Turkish, German, Luxembourgish, Lithuanian, Breton, Romanian, Upper Sorbian, Norwegian, Latvian, Finnish, Lower Sorbian, Spanish, Danish, Slovak, Basque, Swedish, French, Czech, Albanian, Portuguese, Sardinian, Estonian, Icelandic, Dutch, Maltese.

Languages covered with at least 1 exclusive letter (12/41): Hungarian, Portuguese, Lithuanian, Slovak, French, Latvian, Czech, Icelandic, Romanian, Northern Sami, Maltese, German.

Languages not covered (6/41): Manx, Slovenian, Romansh, Irish, Welsh, English.

|Letter|Score|Languages|
|------|-----|---------|
|I ı|4834431|Turkish, Azerbaijani|
|Ã ã|1765649|Portuguese|
|Ñ ñ|893945|Spanish, Galician, Breton, Basque|
|Ł ł|764684|Polish, Upper Sorbian, Lower Sorbian|
|Ă ă|613739|Romanian|
|Ê ê|541865|Western Frisian, French, Portuguese, Breton|
|Ë ë|536131|Dutch, Luxembourgish, French, Albanian|
|Ş ş|265885|Turkish, Azerbaijani|
|Õ õ|262129|Portuguese, Estonian|
|Å å|236832|Swedish, Danish, Norwegian, Finnish|
|Ą ą|204599|Polish, Lithuanian|
|Î î|173851|French, Italian, Romanian, Breton|
|Ý ý|166444|Icelandic, Faroese, Czech, Slovak|
|Ę ę|129649|Polish, Lithuanian|
|Ő ő|123080|Hungarian|
|SS ß|122392|German|
|Ě ě|112048|Czech, Upper Sorbian, Lower Sorbian|
|Ò ò|96051|Italian, Catalan, Corsican, Sardinian|
|Ğ ğ|66382|Turkish, Azerbaijani|
|Ā ā|60329|Latvian|
|Ż ż|59929|Polish, Maltese|
|Ø ø|59228|Danish, Norwegian, Faroese|
|Ș ș|58538|Romanian|
|Œ œ|47397|French|
|Ė ė|45920|Lithuanian|
|Ř ř|44822|Czech, Upper Sorbian, Lower Sorbian|
|Ț ț|35832|Romanian|
|Ś ś|35695|Polish, Lower Sorbian|
|Ì ì|33754|Italian, Corsican, Sardinian|
|Û û|32797|Western Frisian, French, Breton|
|Ï ï|25661|Dutch, French, Catalan, Corsican|
|Ű ű|20129|Hungarian|
|Ų ų|20027|Lithuanian|
|Ť ť|18429|Czech, Slovak|
|Ů ů|14121|Czech|
|Ć ć|13026|Polish, Upper Sorbian, Lower Sorbian|
|Ľ ľ|12605|Slovak|
|Ð ð|12438|Icelandic, Faroese|
|Ń ń|9130|Polish, Upper Sorbian, Lower Sorbian|
|Ħ ħ|9034|Maltese|
|Ī ī|5246|Latvian|
|Į į|4711|Lithuanian|
|Ň ň|4366|Czech, Slovak|
|Ū ū|3556|Lithuanian, Latvian|
|Ď ď|3273|Czech, Slovak|
|Ź ź|2778|Polish, Upper Sorbian, Lower Sorbian|
|Ē ē|1983|Latvian|
|Ġ ġ|1403|Maltese|
|Ċ ċ|722|Maltese|
|Þ þ|710|Icelandic|
|Ĺ ĺ|386|Slovak|
|Ņ ņ|280|Latvian|
|Ŕ ŕ|213|Slovak, Lower Sorbian|
|Ļ ļ|207|Latvian|
|Đ đ|134|Northern Sami|
|Ÿ ÿ|66|French|
|Ķ ķ|65|Latvian|
|Ģ ģ|57|Latvian|
|Ŋ ŋ|44|Northern Sami|
|Ŧ ŧ|4|Northern Sami|
