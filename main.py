from src.search import _web_search_prettify_


user_question = "Ko je Niko Tesla ?"
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