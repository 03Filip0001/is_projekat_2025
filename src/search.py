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
    
    # Izvori pouzdanih informacija
    favored_domains = [
        'wikipedia.org',
        'britannica.com',
        'nationalgeographic.com',
        'nasa.gov',
        'sr.wikipedia.org',
        'rts.rs']
    
    ignored_domains = [
        'instagram.com', 
        'facebook.com', 
        'linkedin.com',                
        'twitter.com', 
        'youtube.com', 
        'pinterest.com', 
        'reddit.com', 
        'informer.rs']
    acceptable_languages = ['sr', 'hr', 'bs', 'en']
    
    # 1. Dobijanje sirovih rezultata
    raw_results = web_search(_user_prompt, 70)
    
    if not raw_results:
        print("Nema rezultata pretrage.")
        return {}

    # 2. Prioritizacija rezultata: favorizovani domeni na prvo mesto
    raw_results.sort(key=lambda x: 1 if urlparse(x['href']).netloc in favored_domains else 2)

    # 3. Ujedinjena petlja za obradu i uklanjanje duplikata
    for result in raw_results:
        if total_found >= _results:
            break
        
        url = result['href']
        
        try:
            domain = urlparse(url).netloc
        except Exception as e:
            print(f"Greška pri parsiranju URL-a {url}: {e}")
            continue

        # Provera da li je domen već obrađen
        if domain in processed_domains:
            print(f"Preskačem duplirani domen: {domain}")
            continue
            
        # Provera da li je URL sa ignorisane liste
        if any(d in domain for d in ignored_domains):
            print(f"Preskačem URL društvene mreže: {url}")
            continue

        text = _process_single_url(url, _user_prompt, acceptable_languages, ignored_domains)
        
        if text:
            prettified_results[url] = text
            processed_domains.add(domain)
            total_found += 1
            print(f"Validan odgovor pronađen: {url}")
            
    return prettified_results

def _process_single_url(url: str, user_prompt: str, acceptable_languages: list, ignored_domains: list):
    """ Pomoćna funkcija za obradu pojedinačnog URL-a
     ne trazi samo <div> dio stranice, vec unutar toga i naslove i podnaslove """
    try:
        domain = urlparse(url).netloc
        if any(d in domain for d in ignored_domains):
            return None

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ciljamo glavni kontejner
            main_content = soup.find(id='content') or \
                           soup.find('main') or \
                           soup.find('div', class_='main') or \
                           soup.find('div', class_='article-body')

            content_to_parse = main_content if main_content else soup.body
            
            if not content_to_parse:
                return None

            # --- NOVO: Pametnije preuzimanje teksta ---
            relevant_text = ""
            prompt_keywords = set(user_prompt.lower().split())

            # Tražimo naslove i paragrafe unutar glavnog kontejnera
            for tag in content_to_parse.find_all(['h1', 'h2', 'h3', 'p']):
                tag_text = tag.get_text(strip=True).lower()
                
                # # Proveravamo da li tekst taga sadrži ključne reči iz upita
                # if any(keyword in tag_text for keyword in prompt_keywords):
                #     # Ako pronađemo podudaranje, uzimamo tekst iz tog taga i njegovog roditelja
                #     relevant_container = tag.find_parent('div') or tag.find_parent('article') or tag.find_parent('section')
                #     if relevant_container:
                #         content_to_parse = relevant_container
                #         break # Izlazimo iz petlje nakon pronalaska relevantnog kontejnera
                #     else:
                #         # Ako ne nađemo roditelja, uzimamo samo tekst iz pronađenog taga
                #         relevant_text = tag.get_text(strip=True)
                #         break

            # Ako nismo pronašli specifičan kontejner, vraćamo se na staru metodu
            if not relevant_text:
                for unwanted_tag in ['script', 'style', 'nav', 'aside', 'footer', 'form', 'img', 'ul', 'li', 'span', 'iframe', 'ins']:
                    for tag in content_to_parse.find_all(unwanted_tag):
                        tag.decompose()
                
                for a_tag in content_to_parse.find_all('a'):
                    a_tag.replace_with(a_tag.text)
                
                page_text = content_to_parse.get_text(separator=' ', strip=True)

                if not page_text or len(page_text.split()) < 50:
                    print(f"Preskačem URL {url} zbog premalog sadržaja.")
                    return None
                
                detected_lang = detect(page_text)
                if detected_lang not in acceptable_languages:
                    print(f"Preskačem URL {url} jer je jezik {detected_lang}")
                    return None

                return page_text
            else:
                return relevant_text

        else:
            print(f"Greška pri preuzimanju URL-a {url}: Status kod {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Greška pri preuzimanju URL-a {url}: {e}")
        return None



if __name__ == '__main__':

    user_question = "Ko je osmislio 'Teoriju relativiteta' ?"
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


    
