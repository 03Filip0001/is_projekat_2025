# TODO Lista

## GUI - Nađa (Ema)
- [X] Napraviti branch pod nazivom "_GUI" od _branch-a "_main_"
- [X] Napraviti "_main.py_" fajl u maticnon (glavnom) folderu projekta
- [X] Pomocu _streamlit_ biblioteke u _Python-u napraviti _GUI - stil po zelji
- [X] Omoguciti _output box_ radi prikaza teksta nakon sto je tekst izgenerisan - u suprotnom je nevidljiv
- [X] Omoguciti _input box_ sa dugmetom "_Generisi_"
- [X] Napraviti dugme "_Obrisi" koje ce da __clear-uje: __input box, __output box_
- [X] Dodati u _requirements.txt_ sve Python biblioteke koje su koriscene (bez verzije) - svaka biblioteka u novi red
  - Primer dodate bibliteke: "_streamlit_"
- [X] Dodati u _.gitignore_ sve fajlove/foldere koji nisu potrebni drugima: _.venv, __pychache_...

## Web Search - KomFi (Minja)
- [X] Napraviti branch pod nazivom "_web_seach" od _branch-a "_main_"
- [X] Napraviti "_search.py" fajl u "src_" folderu projekta
- [X] Napraviti funkciju "_web_search_"
  - Parametri: String _user_prompt, _Int _results_
  - Povratna vrednost: Dictionary { _key=_url, _value=_raw_text}
  - Funkcionalnost: Vraca prvih N (_results) rezultata pretrage korisnikovog pitanja (user_prompt_)
- [X] Dodati funkcionalnost ignorisanja sponzorisanih linkova
- [X] Napraviti funkciju "_web_search_prettify_"
  - Parametri: String _user_prompt, _Int _results_
  - Povratna vrednost: Dictionary { _key=_url, _value=_text}
  - Funkcionalnost: Poziva _web_search_ nakon cega uklanja sponzorstva, slike, linkove... iz teksta
- [X] Dodati u _requirements.txt_ sve Python biblioteke koje su koriscene (bez verzije) - svaka biblioteka u novi red
  - Primer dodate bibliteke: "_requests_"
- [X] Dodati u _.gitignore_ sve fajlove/foldere koji nisu potrebni drugima: _.venv, __pychache_...

 
Krajnji proizvod (funkcija) koju korisnik poziva radi Web Search-a jeste _web_search_prettify_

## Vektorizacija - Ema
- [X] Napraviti branch pod nazivom "_vectors_data" od _branch-a "_main_"
- [X] Napraviti "_vectors_data.py" fajl u "src_" folderu projekta
- [X] Napraviti funkciju "_setup_vectors_"
  - Parametri: Dictionary { _key=_url, _value=_text }
  - Povratna vrednost:  Dictionary { _key=_url, _value= _List { _model, __vectors, __chunk_text_ } }
- [X] Napraviti funkciju "_vectors_search_"
  - Parametri: _model, __vectors, __query, _Int _k_
  - Povratna vrednost: List [ Tupple (_distances, __indices_) ]
- [X] Dodati u _requirements.txt_ sve Python biblioteke koje su koriscene (bez verzije) - svaka biblioteka u novi red
  - Primer dodate bibliteke: "_sentence_transformers_"
- [X] Dodati u _.gitignore_ sve fajlove/foldere koji nisu potrebni drugima: _.venv, __pychache_...

##### Napomene
- Imena parametara: _model, __vectors, __query, __k, __distances, __indices_ nisu fiksna
- Istraziti da li za svaki link da se napravi poseban _model_ tj. _vectors_ ili moze sve preko jednog modela

##### Pomoc pri resavanju
- Repozitorijum [EVDays2025](https://github.com/03Filip0001/EVDays2025.git), fajlovi: train_model.py, search_query.py

## Gemini API - Filip
- [X] Napraviti branch pod nazivom "_prompt_llm" od _branch-a "_main_"
- [X] Napraviti "_prompt_llm.py" fajl u "src_" folderu projekta
- [X] Napraviti funkciju "_prompt_llm_"
  - Parametri: String _user_prompt, _String _context_
  - Povratna vrednost: String _response_
- [X] Dodati u _requirements.txt_ sve Python biblioteke koje su koriscene (bez verzije) - svaka biblioteka u novi red
  - Primer dodate bibliteke: "_sentence_transformers_"
- [X] Dodati u _.gitignore_ sve fajlove/foldere koji nisu potrebni drugima: _.venv, __pychache_...