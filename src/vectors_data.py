from sentence_transformers import SentenceTransformer
import faiss #facebook ai similarity search
import numpy as np
import re

#vektorise tekst
def setup_vectors(prettified_results): 
    """
    Vektorizuje tekstove iz datog rečnika i priprema ih za pretragu.

    Parametri:
    data (dict): Rečnik url : text koji vraca fja _web_search_prettify_

    Povratna vrednost:
    dict: Rečnik sa URL-ovima kao ključevima i listom objekata koji sadrže
          model, FAISS indeks i tekstualne čankove.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    results = {}

    for url, text in prettified_results.items():
        if not text:
            continue
        
        # Konfiguracija za FAISS indeks
        nlist = 35  # Broj klastera (lista) na koje se deli baza
        nprobe = 5  # Broj klastera koji se pretražuju, trazi najblizih 5 centroida
        
        # Deljenje teksta na čankove 
        chunks = chunk_text(text, 400) #eksperimentisi sa ovom vrednoscu

        # Kreiranje vektora (embeddings) za svaki čank
        embeddings = model.encode(chunks)
        
        # Stvaranje FAISS indeksa za efikasnu pretragu
        dimension = embeddings.shape[1]
        quantizer = faiss.IndexFlatL2(dimension)  # Baza za klasterizaciju
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)
        
        # Obuka indeksa (neophodno pre dodavanja vektora)
        if index.is_trained == False:
            index.train(embeddings.astype('float32'))
        
        index.add(embeddings.astype('float32'))
        
        # Postavljanje nprobe parametra za pretragu
        index.nprobe = nprobe
        
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
        for index in indices:
            text_list.append(chunk[index])

        # Dodavanje rezultata u listu kao tuplove
        results_list[url]={
            text_list
        }
            
    return results_list



if __name__ == '__main__':
    print("Sintaksno dobro. Testiraj funkcionalnost")