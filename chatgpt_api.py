import configparser as cfp
from openai import OpenAI
import json

# Model ID
MODEL_ID = 'gpt-3.5-turbo'

# Read the API key from the ini file
key = cfp.ConfigParser()
key.read('openai.ini')

# Create the client
client = OpenAI(
    api_key = key['OPENAI']['api_key']
)

# Save the usage
usage = [0, 0, 0] # [completion_tokens, prompt_tokens, total_tokens]
usage_history = []

def save_usage(usage_arr: list) -> None:
    global usage, usage_history
    usage = [sum(x) for x in zip(usage, usage_arr)]
    usage_history.append(usage.copy())

# Read the default questions from the txt file
def read_default_question(input_str: str) -> list:
    my_data = []
    with open('default_questions.txt', 'r', encoding='utf-8') as f:
        for line in f.read().split('\n'):
            if line != '':
                my_data.append(line.replace('%s', input_str))
    return my_data

def ask_chatgpt(question: str, support_mes: list) -> str:
    support_mes.append(
        {
            "role": "user",
            "content": question,
        }
    )
    chat_completion = client.chat.completions.create(
        messages = support_mes,
        model = MODEL_ID,
        temperature = 0.33
    )

    #save_usage([chat_completion.usage.completion_tokens, chat_completion.usage.prompt_tokens, chat_completion.usage.total_tokens])
    return chat_completion.choices[0].message.content

def first_ask(question) -> str:
    chat_completion = client.chat.completions.create(
        messages = question,
        model = MODEL_ID,
    )

    save_usage([chat_completion.usage.completion_tokens, chat_completion.usage.prompt_tokens, chat_completion.usage.total_tokens])
    return chat_completion.choices[0].message.content

def main() -> None:
    global usage, usage_history
    #question_lines = read_default_question('colorectal cancer')
    question_lines = read_default_question(input('Please input the programming language: '))
    mes = [
        {
            "role": "user",
            "content": question_lines[0],
        }
    ]
    first_response = first_ask(mes).encode('utf-8').decode('utf-8')
    print(first_response)

    mes.append(
        {
            "role": "assistant",
            "content": first_response,
        }
    )

    with open('resp.md', '+a', encoding='utf-8') as f:
        f.write(first_response + '\n\n')

    for question in question_lines[1:]:
        response = ask_chatgpt(question, mes).encode('utf-8').decode('utf-8')
        print(response)

        # Save the response as context
        mes.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        with open('resp.md', '+a', encoding='utf-8') as f:
            f.write(response + '\n\n')

    # Save the output
    #with open('gpt_resp.json', '+w', encoding='utf-8') as f:
    #    f.write(json.dumps(mes))

    for ele in usage_history:
        print('History: '.format(ele))
    print('Total usage: {}'.format(usage))
    return

if __name__ == '__main__':
    main()

# # Test the API key and ask a quation.
# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "you are a nurse, please education the brain cancer patient about brain cancer, including brain function, common syndrom, examination, staging, type, treatment, common chemotherapy drugs, common target grugs, and how to care by themseleves at home by NCCN treatment guideline.",
#         },
#         # {
#         #     "role": "user",
#         #     "content": "Please answer the question in Traditional Chinese.",
#         # }
#     ],
#     model = MODEL_ID,
# )

# # Save the response
# with open('gpt-response.txt', 'a+', encoding='utf-8') as f:
#     f.write('Time: {}; Detail: {}\n'.format(__import__('time').ctime(), chat_completion))
#     for choice in chat_completion.choices:
#         f.write(choice.message.content + '\n')
#     f.write('\n')

