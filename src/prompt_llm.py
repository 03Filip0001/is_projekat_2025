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
	from textwrap import dedent

	final_prompt = dedent(f"""
		You are an expert AI assistant tasked with answering questions based on a provided text.

		Your instructions are:
		- Your response must be based exclusively on the information found in the 'Context' below. Do not use any external knowledge.
		- If the context does not contain the necessary information to answer the question, state that the information is not available in the provided text.
		- Formulate a natural-sounding answer.
		- Write your answer in the same language as the 'Question' (which will be either English or Serbian).
		- Do not mention the context or text in your answer (e.g., avoid phrases like "According to the context...", "Based on text...").

		Context:
		{context}

		Question: {user_prompt}
		Answer:
		""")


	# final_prompt = dedent(f"{user_prompt}")

	response = client.models.generate_content(
			model="gemini-2.5-pro",
			contents=final_prompt
		)
	return response.text