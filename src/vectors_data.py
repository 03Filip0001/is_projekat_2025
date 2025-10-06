from sentence_transformers import SentenceTransformer
import faiss #facebook ai similarity search
import numpy as np
import re

#vektorise tekst
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
        # (pretpostavljamo da funkcija chunk_text postoji i radi)
        chunks = chunk_text(text, 400) 

        # Kreiranje vektora (embeddings) za svaki čank
        embeddings = model.encode(chunks, convert_to_numpy=True)
        dimension = embeddings.shape[1]

        # Automatski biramo FAISS indeks
        if len(chunks) < threshold:
            # Za manje skupove, IndexFlatL2 je optimalan
            # Brz je, ne zahteva trening i pruža 100% preciznost
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            print(f"URL: {url} -> Korišćen IndexFlatL2")
        else:
            # Za veće skupove, koristimo klasterovanje
            nlist = min(35, len(chunks)) 
            nprobe = 5
            
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)
            
            # Treniranje indeksa je neophodno za IVF
            index.train(embeddings)
            index.add(embeddings)
            index.nprobe = nprobe
            print(f"URL: {url} -> Korišćen IndexIVFFlat")

        # Dodavanje u rečnik rezultata
        results[url] = {
            'model': model,
            'vectors': index,
            'chunk_text': chunks
        }
    
    return results

def chunk_text(text, chunk_size=400):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current_chunk = [], []
    current_length = 0
    
    for sentence in sentences:
        tokens = sentence.split()
        if current_length + len(tokens) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.extend(tokens)
        current_length += len(tokens)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks



def vectors_search(query, data, k):
    """
    Pretražuje vektore u FAISS indeksima na osnovu korisničkog upita.

    Parametri:
    data (dict): Rečnik kreiran funkcijom setup_vectors.
    query (str): Korisnički upit.
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
        
        # Pretraga u FAISS indeksu
        distances, indices = vector.search(query_embedding, k)
        
        text_list=[]
        for idx in indices[0]:  # jer indices ima oblik (1, k)
            if idx < len(chunk):  # sigurnosna provera
                text_list.append(chunk[idx])

        # Dodavanje rezultata u listu kao tuplove
        results_list[url] = text_list
        
            
    return results_list



if __name__ == '__main__':
    print("Sintaksno dobro. Testiraj funkcionalnost")