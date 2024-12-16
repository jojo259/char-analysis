import wikipediaapi
from openai import OpenAI
import requests
import time
from langcodes import Language
import config
import os
import tiktoken
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def fetch_wikipedia_page(language_name):
    wiki = wikipediaapi.Wikipedia('python-bot')
    page = wiki.page(f"{language_name} alphabet")
    if page.exists():
        print(f'got alphabet wikipedia page {page} for {language_name}')
    else:
        page = wiki.page(f"{language_name} orthography")
        if page.exists():
            print(f'got wikipedia orthography page {page} for {language_name}')
        else:
            page = wiki.page(f"{language_name} language")
            if page.exists():
                print(f'got wikipedia language page {page} for {language_name}')
            else:
                page = wiki.page(language_name)
                if page.exists():
                    print(f'got wikipedia plain name page {page} for {language_name}')
    if page.exists():
        return page.fullurl
    return None

def fetch_page_html(url):
    print(f'fetching url {url}')
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def tokenize(text):
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    encoded = enc.encode(text)
    return encoded

def get_tokens_length(text):
    return len(tokenize(text))

def truncate_tokens(text, max_length):
    tokenized = tokenize(text)
    while len(tokenized) > max_length:
        text = text[:int(-(len(text) * 0.1))]
        tokenized = tokenize(text)
    return text

def extract_alphabet_letters(language_name, language_code, html_content):
    print(f'truncating html for {language_name} ({language_code})')
    html_content = truncate_tokens(html_content, 124_000)

    prompt = (
        f"HTML:\n```{html_content}\n```"
        f"\n\nThis is the HTML content of a Wikipedia page about the {language_name} alphabet or orthography."
        "\nPlease extract and return a list of the letters used in this alphabet."
        "\nReturn only lowercase characters."
        "\nInclude letters with diacritic marks or other special letters if they are official letters or letters in common use that you would see in the wild."
        "\nInclude letters with diacritic marks if they are in use, regardless of whether they are officially letters (e.g. the marks are used to indicate stress)"
        "\nReturn the list as in JSON format with the top-level key being just \"letters\"."
        "\nDO NOT surround the JSON with triple grave accents (```)."
        "\nReturn ONLY the JSON. DO NOT write any messages along with the JSON."
    )

    print(f'prompting for {language_name} ({language_code}) with token length {get_tokens_length(prompt)}')

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )
    print(response)
    return response.choices[0].message.content.strip()

def write_results_to_file(language_code, results, filename):
    os.makedirs("letters", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(results)
    print(f"Results for {language_code} written to {filename}")


def get_language_name(lang_code):
    if lang_code == "fry":
        return "West Frisian"
    if lang_code == "wen":
        return "Sorbian"
    if lang_code == "xal":
    	return "Kalmyk Oirat"
    return Language.get(language_code).display_name()

def main(language_code, filename):
    language_name = get_language_name(language_code)
    print(f"Processing {language_name} ({language_code})")
    url = fetch_wikipedia_page(language_name)
    if url:
        html_content = fetch_page_html(url)
        if html_content:
            letters = extract_alphabet_letters(language_name, language_code, html_content)
            print(f"\nAlphabet for {language_code}:\n{letters}\n")
            write_results_to_file(language_code, letters, filename)
            return
        else:
            print(f"Failed to fetch HTML for {language_code}.")
    else:
        print(f"No Wikipedia page found for {language_code} alphabet/orthography.")
        return
    raise Exception(f'failed to run for {language}')

if __name__ == "__main__":
    for language_code in config.languages:
        filename = f"letters/{language_code}-letters.txt"
        if os.path.exists(filename):
            print(f"File {filename} already exists. Skipping {language_code}...")
            continue
        main(language_code, filename)
