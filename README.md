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
- Create a CSV for memorisation with Anki

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
- `extra_language_deweight`: `1` - score multiplier calculated as an exponent based on the number of languages a letter is used in (default is 1 but can be lowered if multiple-language letters should be deranked)

### Corpus

- `corpus_types`: `wikipedia` - source for corpus
- `corpus_sizes`: `100k, 10k` - size in bytes for corpora to download
- `corpus_years`: `2024 to 2000` - years to check for corpora

### Alphabets

- `OPENAI_API_KEY` - OpenAI API key for regenerating language alphabets (already included in-repo)

### Data sources

- Corpora: The Leipzig Corpora Collection © 2024 Universität Leipzig / Sächsische Akademie der Wissenschaften / InfAI
- Language speaker count: Wikidata
- Language alphabets: Wikipedia pages on language alphabets, orthographies, or their general language pages, processed with ChatGPT-4o mini

## Results (default parameters)

Covers 60 letters out of 104 total for 41 languages.

Naive score is the letter's score without taking into account any deweightings.

Languages covered with at least 1 letter (35/41): Western Frisian, French, Norwegian, Italian, Latvian, Azerbaijani, Polish, Faroese, Portuguese, Sardinian, Lithuanian, Hungarian, Romanian, Corsican, Luxembourgish, Icelandic, Maltese, Catalan, Northern Sami, Estonian, Swedish, Breton, Danish, Slovak, German, Dutch, Albanian, Czech, Turkish, Lower Sorbian, Galician, Upper Sorbian, Basque, Spanish, Finnish.

Languages covered with at least 1 exclusive letter (12/41): Maltese, Hungarian, Lithuanian, Romanian, French, Czech, Northern Sami, Latvian, Portuguese, Slovak, Icelandic, German.

Languages not covered (6/41): Slovenian, Irish, Manx, English, Welsh, Romansh.

Rank|Letter|Naive score|Languages|
|----|------|-----------|---------|
1|I ı|4834|Turkish, Azerbaijani|
2|Ã ã|1766|Portuguese|
3|Ñ ñ|894|Spanish, Galician, Breton, Basque|
4|Ł ł|765|Polish, Upper Sorbian, Lower Sorbian|
5|Ă ă|614|Romanian|
6|Ê ê|631|Western Frisian, French, Portuguese, Breton|
7|Ë ë|536|Dutch, Luxembourgish, French, Albanian|
8|Ş ş|1710|Turkish, Azerbaijani|
9|Õ õ|362|Portuguese, Estonian|
10|Å å|237|Swedish, Danish, Norwegian, Finnish|
11|Ą ą|416|Polish, Lithuanian|
12|Î î|350|French, Italian, Romanian, Breton|
13|Ý ý|166|Icelandic, Faroese, Czech, Slovak|
14|Ę ę|407|Polish, Lithuanian|
15|Ő ő|123|Hungarian|
16|SS ß|122|German|
17|Ě ě|162|Czech, Upper Sorbian, Lower Sorbian|
18|Ò ò|96|Italian, Catalan, Corsican, Sardinian|
19|Ğ ğ|850|Turkish, Azerbaijani|
20|Ā ā|60|Latvian|
21|Ż ż|273|Polish, Maltese|
22|Ø ø|87|Danish, Norwegian, Faroese|
23|Ș ș|254|Romanian|
24|Œ œ|51|French|
25|Ė ė|64|Lithuanian|
26|Ř ř|119|Czech, Upper Sorbian|
27|Ț ț|237|Romanian|
28|Ś ś|226|Polish, Lower Sorbian|
29|Ì ì|36|Italian, Corsican, Sardinian|
30|Û û|36|Western Frisian, French, Breton|
31|Ï ï|28|Dutch, French, Catalan, Corsican|
32|Ű ű|30|Hungarian|
33|Ų ų|53|Lithuanian|
34|Ť ť|31|Czech, Slovak|
35|Ů ů|59|Czech|
36|Ć ć|104|Polish, Upper Sorbian, Lower Sorbian|
37|Ľ ľ|24|Slovak|
38|Ð ð|15|Icelandic, Faroese|
39|Ń ń|81|Polish, Upper Sorbian, Lower Sorbian|
40|Ħ ħ|12|Maltese|
41|Ī ī|27|Latvian|
42|Į į|22|Lithuanian|
43|Ň ň|13|Czech, Slovak|
44|Ū ū|23|Lithuanian, Latvian|
45|Ď ď|9|Czech, Slovak|
46|Ź ź|27|Polish, Upper Sorbian, Lower Sorbian|
47|Ē ē|25|Latvian|
48|Ġ ġ|5|Maltese|
49|Ċ ċ|3|Maltese|
50|Þ þ|4|Icelandic|
51|Ĺ ĺ|1|Slovak|
52|Ņ ņ|7|Latvian|
53|Ŕ ŕ|1|Slovak, Lower Sorbian|
54|Ļ ļ|6|Latvian|
55|Đ đ|0|Northern Sami|
56|Ÿ ÿ|0|French|
57|Ķ ķ|2|Latvian|
58|Ģ ģ|2|Latvian|
59|Ŋ ŋ|0|Northern Sami|
60|Ŧ ŧ|0|Northern Sami|
