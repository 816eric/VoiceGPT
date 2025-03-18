class GPTClient:
    def __init__(self, api_key):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def send_question(self, question):
        print(question)
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": question}]
        )
        return completion.choices[0].message.content

    def receive_response(self, question):
        return self.send_question(question)