import openai

class OpenAIClient(object):
    def __init__(self, model :str="gpt-4"):
        self.openai = openai.OpenAI()
        self.model = model
    
    def _get_prompt(self, query):
        prompt = f"""
        Extract details from query: '{query}'
        """

        return prompt
    
    def extract(self, query):
        response = self.openai.chat.completions.create(
                                                    model="gpt-4o",
                                                    messages=[
                                                        {"role": "user", "content": self._get_prompt(query)}
                                                        ],
                                                    temperature=0  
                                                )
        content = response.choices[0].message.content
        print(content)
        return content