from openai import OpenAI
class OpenAIText:
    def OpenAITextResponse(query:str, content:str):
        #testKey = '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'
        keyValue=''
        client = OpenAI(api_key=keyValue)

        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": query
            },
            {
            "role": "user",
            "content": content
            }
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content 
        