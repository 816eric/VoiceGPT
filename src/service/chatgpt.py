from openai import OpenAI

class GPTClient:
    def __init__(self, api_key=None, model=None):
        """
        Initializes the GPTClient with your OpenAI API key.
        
        Parameters:
          api_key (str): Your OpenAI API key.
          model (str): The model to use, e.g. "gpt-3.5-turbo" or "gpt-4". Default is "gpt-3.5-turbo".
        """
        #if api_key is empty or none then use the default key
        if api_key is None or api_key == "":
            api_key = "your api key here"
        self.api_key = api_key
        #if model is empty or none then use the default model
        if model is None or model == "":
            model = "gpt-4o-mini"
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def ask(self, question, system_prompt="You are a helpful assistant."):
        """
        Sends a question to ChatGPT and returns the response.
        
        Parameters:
          question (str): The question or prompt for ChatGPT.
          system_prompt (str): (Optional) A system prompt to set the assistant's behavior.
        
        Returns:
          str: The ChatGPT response.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                store=True,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                temperature=0.7  # You can adjust the temperature if needed
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred: {e}"

# Example usage:
if __name__ == "__main__":
    api_key = None
    client = GPTClient(api_key)
    
    print("Enter your questions (type 'quit' to exit):")
    while True:
        question = input("You: ")
        if question.lower() == "quit":
            break
        answer = client.ask(question)
        print("ChatGPT:", answer)
