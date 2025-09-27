#googlesearch-python
""" Pretražuje DuckDuckGo pretraživač koristeći DuckDuckGoSearch klasu i korisnikov upit.
Dobija URL-ove i kratak opis prvih N rezultata.
Posećuje svaki od tih URL-ova.
Parsira HTML sadržaj stranice da bi izvukla sirov tekst.
Vraća rečnik gde je ključ URL, a vrednost sirov tekst stranice. """

from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from langdetect import detect, DetectorFactory

def web_search(_user_prompt: str, _results: int) -> dict:
    """
    Pretražuje internet i vraća sirov tekst sa prvih N rezultata.

    Parametri:
    _user_prompt (str): Upit za pretragu.
    _results (int): Broj rezultata koje treba vratiti.

    Povratna vrednost:
    dict: Rečnik gde je ključ URL, a vrednost sirov tekst stranice.
    """
    search_results = {}
    
    with DDGS() as ddgs:
        ddgs_results = ddgs.text(keywords=_user_prompt, max_results=_results)
        
        for result in ddgs_results:
            url = result['href']
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = ' '.join([p.get_text() for p in soup.find_all('p')])
                    search_results[url] = page_text
                else:
                    search_results[url] = None
            except requests.exceptions.RequestException:
                search_results[url] = None
                
    return search_results

# Postavljanje sed-a za langdetect radi konzistentnosti
DetectorFactory.seed = 0

def _web_search_prettify_(_user_prompt: str, _results: int) -> dict:
    """
    Pretražuje internet dok ne pronađe traženi broj validnih, pročišćenih
    rezultata na srpskom jeziku, uklanjajući duplikate i irelevantne sajtove.

    Parametri:
    _user_prompt (str): Upit za pretragu.
    _results (int): Broj validnih rezultata koje treba vratiti.

    Povratna vrednost:
    dict: Rečnik gde je ključ URL, a vrednost pročišćen tekst stranice.
    """
    prettified_results = {}
    processed_domains = set()
    total_found = 0
    search_offset = 0  # Koristi se za pretragu u serijama

    acceptable_languages = ['sr', 'hr'] #ove jezike prihvatam, u suprotnom mozda necu dobiti odg ni nakon 20 pretraga

    # Lista domena koje treba ignorisati
    ignored_domains = ['instagram.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'youtube.com']
    
    with DDGS() as ddgs:
        # Ponavljamo pretragu sve dok ne pronađemo traženi broj rezultata
        while total_found < _results:
            print(f"Tražim novu seriju rezultata (ukupno pronađeno: {total_found}/{_results})...")
            
            # Pretraga bez jezičkog filtera u upitu
            ddgs_results = ddgs.text(query=_user_prompt, max_results=20, safesearch='off')

            if not ddgs_results:
                print("Nema više rezultata za pretragu. Prekidam.")
                break

            for result in ddgs_results:
                if total_found >= _results:
                    break

                url = result['href']
                
                try:
                    domain = urlparse(url).netloc
                    if domain in processed_domains:
                        print(f"Preskačem duplirani domen: {domain}")
                        continue
                except Exception as e:
                    print(f"Greška pri parsiranju URL-a {url}: {e}")
                    continue

                if any(d in domain for d in ignored_domains):
                    print(f"Preskačem URL društvene mreže: {url}")
                    continue

                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers, timeout=5)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        for unwanted_tag in ['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'img']:
                            for tag in soup.find_all(unwanted_tag):
                                tag.decompose()
                        
                        for a_tag in soup.find_all('a'):
                            a_tag.replace_with(a_tag.text)
                        
                        page_text = soup.get_text(separator=' ', strip=True)

                        if not page_text or len(page_text.split()) < 50:
                            print(f"Preskačem URL {url} zbog premalog sadržaja.")
                            continue

                        # --- PROVERA JEZIKA ---
                        detected_lang = detect(page_text)
                        if detected_lang not in acceptable_languages:
                            print(f"Preskačem URL {url} jer je jezik {detected_lang}")
                            continue

                        prettified_results[url] = page_text
                        processed_domains.add(domain)
                        total_found += 1
                        print(f"Validan odgovor pronađen: {url}")
                    else:
                        print(f"Greška pri preuzimanju URL-a {url}: Status kod {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Greška pri preuzimanju URL-a {url}: {e}")
    
    return prettified_results


if __name__ == '__main__':
# --- GLAVNI DEO PROGRAMA ---
    user_question = "Ko je Nikola Tesla lang:sr"
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


    
