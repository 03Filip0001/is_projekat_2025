from sentence_transformers import SentenceTransformer
import faiss  # facebook ai similarity search
import numpy as np
import re


def setup_vectors(prettified_results):
    """
    Vektorizuje tekstove iz datog rečnika i priprema ih za pretragu,
    automatski birajući optimalan FAISS indeks na osnovu veličine teksta.

    Parametri:
    prettified_results (dict): Rečnik url : text.

    Povratna vrednost:
    dict: Rečnik sa URL-ovima kao ključevima i listom objekata koji sadrže
          model, FAISS indeks i tekstualne čankove.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    results = {}
    
    # Granica za prebacivanje na IndexIVFFlat
    # Za manje od 100 čankova, IndexFlatL2 je brži i precizniji
    threshold = 100 

    for url, text in prettified_results.items():
        if not text:
            continue
        
        # Deljenje teksta na čankove 
        chunks = chunk_text(text, chunk_size=400)
        
        if not chunks:
            continue
        
        # Vektorizacija čankova
        embeddings = model.encode(chunks, convert_to_numpy=True).astype("float32")
        
        # Kreiranje FAISS indeksa
        dimension = embeddings.shape[1]
        
        if len(chunks) < threshold:
            # Za manji broj čankova koristimo prost IndexFlatL2
            index = faiss.IndexFlatL2(dimension)
        else:
            # Za veći broj čankova koristimo IndexIVFFlat
            nlist = min(int(np.sqrt(len(chunks))), 100)
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            index.train(embeddings)
        
        # Dodavanje vektora u indeks
        index.add(embeddings)
        
        # Čuvanje podataka
        results[url] = {
            'model': model,
            'vectors': index,
            'chunk_text': chunks
        }
    
    return results


def chunk_text(text, chunk_size=400):
    """
    Deli tekst na čankove određene veličine, pokušavajući da čuva granice rečenica.
    
    Parametri:
    text (str): Tekst koji treba podeliti.
    chunk_size (int): Približna veličina svakog čanka u karakterima.
    
    Povratna vrednost:
    list: Lista tekstualnih čankova.
    """
    if not text or not text.strip():
        return []
    
    # Deljenje po rečenicama
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Ako dodavanje rečenice ne bi prekoračilo chunk_size, dodaj je
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            # Ako trenutni čank nije prazan, dodaj ga u listu
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            # Započni novi čank sa trenutnom rečenicom
            current_chunk = sentence + " "
    
    # Dodaj poslednji čank ako postoji
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def vectors_search(query, data, k):
    """
    Pretražuje vektore u FAISS indeksima na osnovu korisničkog upita.

    Parametri:
    query (str): Korisnički upit.
    data (dict): Rečnik kreiran funkcijom setup_vectors.
    k (int): Broj najsličnijih rezultata koje treba vratiti.

    Povratna vrednost:
    dict: url : najrelevatniji tekst
    """
    results_list = {}
    
    for url, vectors_data in data.items():
        model = vectors_data['model']
        chunk = vectors_data['chunk_text']
        vector = vectors_data['vectors']
        
        # Vektorizacija korisničkog upita
        query_embedding = model.encode([query]).astype("float32")
        
        # Ograničavanje k na broj dostupnih čankova
        actual_k = min(k, len(chunk))
        
        # Pretraga u FAISS indeksu
        distances, indices = vector.search(query_embedding, actual_k)
        
        text_list = []
        for idx in indices[0]:  # jer indices ima oblik (1, k)
            if idx < len(chunk):  # sigurnosna provera
                text_list.append(chunk[idx])

        # Dodavanje rezultata u listu kao tuplove
        results_list[url] = text_list
        
            
    return results_list


if __name__ == '__main__':
    print("Sintaksno dobro. Testiraj funkcionalnost")
