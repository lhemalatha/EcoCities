from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.prompts import PromptTemplate

def generate_recycling_idea(user_input: str, max_tokens: int = 512, temperature: float = 0.3):
    """
    Generates a creative idea for reusing or recycling a product based on the user's input.

    Parameters:
    - user_input (str): The item or products the user wants to recycle or reuse.
    - max_tokens (int): Maximum number of tokens for the generated response (default is 150).
    - temperature (float): Controls the randomness of the response (default is 0.3, lower values reduce randomness).

    Returns:
    - str: A creative idea and instructions for reusing or recycling the input item(s).
    """
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")

    # Define the modified prompt template to only ask for the output
    prompt_template = """
    Suggest a practical, creative, and aesthetically pleasing way to reuse or recycle the following item(s). Provide a brief 5-line response with steps or suggestions.

    User input: {user_input}
    """
#     prompt_template = """
# Suggest a practical, creative, and aesthetically pleasing way to reuse or recycle the following item(s). Also, provide advice on whether the item is biodegradable or not and how to dispose of it properly. Include steps or suggestions in a brief 5-line response.

# User input: {user_input}
# """

    # Create the Langchain prompt template
    template = PromptTemplate(input_variables=["user_input"], template=prompt_template)

    # Format the prompt with the user's input
    prompt = template.format(user_input=user_input)

    # Use the text generation pipeline with custom temperature and max tokens, and enable sampling
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, config={"do_sample": True, "temperature": temperature})

    # Generate a response based on the formatted prompt
    response = pipe(prompt, max_new_tokens=max_tokens, truncation=True)

    # Return only the model's creative output
    return response[0]['generated_text'].strip()
