from google import genai
from textwrap import dedent

def prompt_llm(user_prompt=None, context_text=None, api_key=None):
	"""
		Ova funkcija postavlja pitanje LLM-u na internetu i vraca odgovor na osnovu prosledjenog konteksta

		Parametri:

		user_prompt -> Korisnikovo pitanje

		context_text -> Kontekst na osnovu kog LLM odgovara

		api_key -> Kljuc kako bi pristupili LLM-u
	"""

	if api_key is None:
		raise ValueError("Please provide API_KEY for GEMINI")
	
	if (user_prompt is None) or (context_text is None):
		raise ValueError("Provide user_prompt and context_text")

	client = genai.Client(api_key=api_key)

	context = "\n" + context_text
	final_prompt = dedent(f"""
	You are a helpful assistant. Use the following context to answer the question.
	Answer only based on context. Use English or Serbian for your answer.

	Context:
	{context}

	Question: {user_prompt}
	Answer:
	""")

	# final_prompt = dedent(f"{user_prompt}")

	response = client.models.generate_content(
			model="gemini-2.5-flash-lite",
			contents=final_prompt
		)
	return response.text