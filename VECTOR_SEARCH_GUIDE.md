# Vector Search Guide - Najbolja poklapanja za Gemini model

## Pregled

Modul `src/vectors_data.py` implementira funkcionalnost za pronalaženje najrelevantnijih delova teksta koji odgovaraju na korisničko pitanje. Ove funkcije koriste **vektorsku pretragu** da identifikuju najbolja poklapanja koja će biti prosleđena Gemini modelu za generisanje odgovora.

## Funkcije

### 1. `chunk_text(text, chunk_size=400)`

Deli tekst na manje delove (chunks) održavajući granice rečenica.

**Parametri:**
- `text` (str): Tekst za deljenje
- `chunk_size` (int): Maksimalna veličina čanka u karakterima (default: 400)

**Vraća:**
- Lista tekstualnih čankova

**Primer:**
```python
from src.vectors_data import chunk_text

tekst = "Nikola Tesla je bio srpski pronalazač. Radio je na razvoju naizmenične struje. Njegovo delo je revolucionizovalo elektrotehniku."
chunks = chunk_text(tekst, chunk_size=100)
# Rezultat: ['Nikola Tesla je bio srpski pronalazač. Radio je na razvoju naizmenične struje.', 
#            'Njegovo delo je revolucionizovalo elektrotehniku.']
```

### 2. `setup_vectors(prettified_results)`

Vektorizuje tekstove i priprema FAISS indeks za pretragu.

**Parametri:**
- `prettified_results` (dict): Rečnik gde je ključ URL, a vrednost tekst stranice

**Vraća:**
- Dictionary: `{url: {'model': model, 'vectors': faiss_index, 'chunk_text': chunks}}`

**Primer:**
```python
from src.vectors_data import setup_vectors

# Pretpostavimo da već imamo tekstove sa web pretrage
context = {
    "https://example.com/tesla": "Nikola Tesla bio je srpski naučnik...",
    "https://example.com/einstein": "Albert Einstein bio je fizičar..."
}

vectors = setup_vectors(context)
# Vektorizovani podaci spremni za pretragu
```

### 3. `vectors_search(query, data, k)`

Pretražuje vektore i vraća k najrelevantnijih tekstova za dati upit.

**Parametri:**
- `query` (str): Korisničko pitanje
- `data` (dict): Vektorizovani podaci iz `setup_vectors()`
- `k` (int): Broj najboljih poklapanja koje treba vratiti po URL-u

**Vraća:**
- Dictionary: `{url: [lista najrelevantnijih tekstova]}`

**Primer:**
```python
from src.vectors_data import vectors_search

best_matches = vectors_search(
    query="Ko je Nikola Tesla?",
    data=vectors,
    k=3
)

# Rezultat: {'https://example.com/tesla': ['Nikola Tesla bio je srpski naučnik...', ...]}
```

## Kompletan primer korišćenja

```python
from src.search import _web_search_prettify_
from src.vectors_data import setup_vectors, vectors_search
from src.prompt_llm import prompt_llm

# Korak 1: Korisnički upit
user_question = "Kada je rođen Nikola Tesla?"

# Korak 2: Pretraga interneta
print("Pretražujem internet...")
web_results = _web_search_prettify_(user_question, _results=5)

# Korak 3: Vektorizacija pronađenih tekstova
print("Vektorizujem tekstove...")
vectors = setup_vectors(web_results)

# Korak 4: Pronalaženje najboljih poklapanja
print("Tražim najrelevantnije informacije...")
best_matches = vectors_search(query=user_question, data=vectors, k=3)

# Korak 5: Priprema konteksta za Gemini
context_text = ""
for url, text_chunks in best_matches.items():
    for chunk in text_chunks:
        context_text += "\n\n" + chunk

# Korak 6: Generisanje odgovora pomoću Gemini modela
answer = prompt_llm(
    user_prompt=user_question,
    context_text=context_text,
    api_key="YOUR_API_KEY"
)

print(f"Odgovor: {answer}")
```

## Kako funkcioniše?

### Vektorska reprezentacija teksta

1. **Svaka rečenica/čank** se pretvara u numerički vektor (niz brojeva) koristeći Sentence Transformer model
2. **Slični tekstovi** imaju slične vektore - ovo nam omogućava da matematički merimo sličnost
3. **FAISS** brzo pretražuje milione vektora da pronađe najsličnije

### Zašto je ovo važno za Gemini?

- **Filtrira nerelevantne informacije**: Umesto da šaljemo celu web stranicu, šaljemo samo relevantne delove
- **Fokusiran kontekst**: Gemini dobija tačno ono što mu treba da odgovori na pitanje
- **Bolji odgovori**: Sa relevantnim kontekstom, Gemini generiše preciznije i tačnije odgovore
- **Efikasnost**: Manje podataka = brži odgovori i niži troškovi

## Tehnička implementacija

- **Model**: `all-MiniLM-L6-v2` - kompaktan i brz model za engleske i srpske tekstove
- **FAISS Index**: 
  - `IndexFlatL2` za male količine podataka (< 100 čankova)
  - `IndexIVFFlat` za velike količine podataka (>= 100 čankova)
- **Chunk size**: 400 karaktera - balans između konteksta i preciznosti

## Zavisnosti

```
sentence-transformers  # Za vektorsku reprezentaciju teksta
faiss-cpu             # Za brzu pretragu vektora
numpy                 # Za numeričke operacije
```

## Napomene

- Model se automatski preuzima sa HuggingFace pri prvom pokretanju
- FAISS indeks se kreira u memoriji i nije persistentan
- Za produkciju, razmotri keširање modela i indeksa
