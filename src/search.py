from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from langdetect import detect, DetectorFactory

def web_search(_user_prompt: str, _results: int) -> dict:
    """
    Vrši pretragu interneta i vraća listu sirovih rezultata od DuckDuckGo-a.
    
    Parametri:
    _user_prompt (str): Upit za pretragu.
    _results (int): Broj rezultata za pretragu.

    Povratna vrednost:
    list: Lista sirovih rezultata pretrage.
    """
    with DDGS() as ddgs:
        ddgs_results = ddgs.text(query=_user_prompt, max_results=_results, safesearch='off')
        return ddgs_results

# Postavljanje sed-a za langdetect radi konzistentnosti
DetectorFactory.seed = 0

def _web_search_prettify_(_user_prompt: str, _results: int) -> dict:
    """
    Preuzima sirove rezultate pretrage, čisti ih i filtrira, vraćajući
    traženi broj validnih odgovora.
    
    Parametri:
    _user_prompt (str): Upit za pretragu.
    _results (int): Broj validnih rezultata koje treba vratiti.

    Povratna vrednost:
    dict: Rečnik gde je ključ URL, a vrednost pročišćen tekst stranice.
    """
    prettified_results = {}
    processed_domains = set()
    total_found = 0
    
    # Podaci za filtriranje
    favored_domains = [
        'wikipedia.org',
        'britannica.com',
        'nationalgeographic.com',
        'nasa.gov',
        'sr.wikipedia.org',
        'rts.rs',
        'tesla-duhovni-lik.rs'
    ]
    ignored_domains = ['instagram.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'youtube.com']
    acceptable_languages = ['sr', 'hr', 'bs']
    
    # 1. Pozivanje web_search za dobijanje sirovih rezultata
    raw_results = web_search(_user_prompt, 30)
    
    if not raw_results:
        print("Nema rezultata pretrage.")
        return {}
    
    unprocessed_results = []
    
    # PRVA FAZA: Prioritizacija favorizovanih domena
    for result in raw_results:
        url = result['href']
        try:
            domain = urlparse(url).netloc
            if domain in favored_domains:
                if domain not in processed_domains:
                    text = _process_single_url(url, acceptable_languages, ignored_domains)
                    if text:
                        prettified_results[url] = text
                        processed_domains.add(domain)
                        print(f"Pronađen favorizovani odgovor: {url}")
                        if len(prettified_results) >= _results:
                            return prettified_results
            else:
                unprocessed_results.append(result)
        except Exception as e:
            print(f"Greška pri parsiranju URL-a {url}: {e}")
            
    # DRUGA FAZA: Obrada preostalih rezultata
    print("Prioritetna pretraga završena. Nastavljam sa standardnom pretragom.")
    for result in unprocessed_results:
        if len(prettified_results) >= _results:
            break
        
        url = result['href']
        try:
            domain = urlparse(url).netloc
            if domain in processed_domains:
                continue

            text = _process_single_url(url, acceptable_languages, ignored_domains)
            if text:
                prettified_results[url] = text
                processed_domains.add(domain)
                print(f"Pronađen standardni odgovor: {url}")
        except Exception as e:
            print(f"Greška pri parsiranju URL-a {url}: {e}")
    
    return prettified_results

def _process_single_url(url: str, acceptable_languages: list, ignored_domains: list) -> str or None:
    """ Pomoćna funkcija za obradu pojedinačnog URL-a. """
    try:
        domain = urlparse(url).netloc
        if any(d in domain for d in ignored_domains):
            print(f"Preskačem URL društvene mreže: {url}")
            return None

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            main_content = soup.find(id='content') or \
                           soup.find('main') or \
                           soup.find('div', class_='main') or \
                           soup.find('div', class_='article-body')

            content_to_parse = main_content if main_content else soup.body
            
            if not content_to_parse:
                return None

            unwanted_tags = ['script', 'style', 'nav', 'aside', 'footer', 'form', 'img', 'ul', 'li', 'span']
            for unwanted_tag in unwanted_tags:
                for tag in content_to_parse.find_all(unwanted_tag):
                    tag.decompose()
            for a_tag in content_to_parse.find_all('a'):
                a_tag.replace_with(a_tag.text)
            
            page_text = content_to_parse.get_text(separator=' ', strip=True)

            if not page_text or len(page_text.split()) < 50:
                return None
            
            detected_lang = detect(page_text)
            if detected_lang not in acceptable_languages:
                return None

            return page_text
        else:
            print(f"Greška pri preuzimanju URL-a {url}: Status kod {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Greška pri preuzimanju URL-a {url}: {e}")
        return None



if __name__ == '__main__':
# --- GLAVNI DEO PROGRAMA ---
    user_question = "Ko je Ivo Andric?"
    number_of_results = 3
    file_name = "rezultati_pretrage.txt"

    # Korak 1: Pozivanje funkcije pretrage
    # Pozivanje nove funkcije
    results_dict = _web_search_prettify_(user_question, number_of_results)
    
    # Pisanje u fajl
    with open(file_name, "w", encoding="utf-8") as f:
        if results_dict:
            for url, text in results_dict.items():
                f.write(f"URL: {url}\n")
                f.write("--- Pročišćen Sadržaj ---\n")
                f.write(text)
                f.write("\n" + "-" * 50 + "\n\n")
        else:
            f.write("Nema pronađenih rezultata za ovaj upit.\n")
    
    print(f"Pretraga završena. Rezultati su snimljeni u fajl '{file_name}'.")


    
