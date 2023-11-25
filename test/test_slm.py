import autogen

config_list = [
    {
        "base_url": "http://localhost:1234/v1",
        "api_key": "xyz"
    }
]

# llm_config={
#     "config_list": config_list,
#     "temperature": 0
# }

# # create an AssistantAgent instance named "assistant"
# assistant = autogen.AssistantAgent(
#     name="assistant",
#     system_message= "You are a helpful assistant. You write Python code to solve a task.",
#     llm_config=llm_config,
#     # system_message="AI agent"
# )
# # create a UserProxyAgent instance named "user_proxy"
# user_proxy = autogen.UserProxyAgent(
#     name="user_proxy",
#     human_input_mode="ALWAYS",
#     max_consecutive_auto_reply=10,
#     code_execution_config={"use_docker": False },
# )

# user_proxy.initiate_chat(
#     assistant,
#     message="Write a profile for Gagan Bansal. You can find his information online via https://gagb.github.io/."
# )

# llm_config = {
#     "functions": [
#         {
#             "name": "python",
#             "description": "run cell in ipython and return the execution result.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "cell": {
#                         "type": "string",
#                         "description": "Valid Python cell to execute.",
#                     }
#                 },
#                 "required": ["cell"],
#             },
#         },
#         {
#             "name": "sh",
#             "description": "run a shell script and return the execution result.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "script": {
#                         "type": "string",
#                         "description": "Valid shell script to execute.",
#                     }
#                 },
#                 "required": ["script"],
#             },
#         },
#     ],
#     "config_list": config_list,
#     "timeout": 120,
# }

llm_config = {
    "functions": [
        {
            "name": "news",
            "description": "Get the latest news from Yahoo News.",
        },
    ],
    "config_list": config_list,
    "timeout": 120,
}
chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
)

# define functions according to the function description
from IPython import get_ipython

def exec_python(cell):
    ipython = get_ipython()
    result = ipython.run_cell(cell)
    log = str(result.result)
    if result.error_before_exec is not None:
        log += f"\n{result.error_before_exec}"
    if result.error_in_exec is not None:
        log += f"\n{result.error_in_exec}"
    return log

def exec_sh(script):
    return user_proxy.execute_code_blocks([("sh", script)])

def get_latest_yahoo_news():
    # URL of Yahoo News
    url = 'https://news.yahoo.com/'

    # Sending a request to the website
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to retrieve news"

    # Parsing the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Finding news items - assuming they are under <h3> tags with class 'Mb(5px)'
    news_items = soup.find_all('h3', class_='Mb(5px)')

    # Extracting the first 5 news titles and URLs
    news_list = []
    for item in news_items[:5]:
        title = item.text.strip()
        link = item.find('a', href=True)['href']
        news_list.append({'title': title, 'link': link})
    if not news_list:
        return "Failed to retrieve news"
    return news_list

# register the functions
chatbot.register_function(
    function_map={
        "news": get_latest_yahoo_news,
    }
)

task = """
Get the latest news from Yahoo News. You can use function calls get_latest_yahoo_news to get the news.

Save the code below to a file named yahoo_news.py so that we can run the code from this file.
```python
def get_latest_yahoo_news():
    # URL of Yahoo News
    url = 'https://news.yahoo.com/'

    # Sending a request to the website
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to retrieve news"

    # Parsing the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Finding news items - assuming they are under <h3> tags with class 'Mb(5px)'
    news_items = soup.find_all('h3', class_='Mb(5px)')

    # Extracting the first 5 news titles and URLs
    news_list = []
    for item in news_items[:5]:
        title = item.text.strip()
        link = item.find('a', href=True)['href']
        news_list.append({'title': title, 'link': link})
    if not news_list:
        return "Failed to retrieve news"
    return news_list
```
"""
# start the conversation
user_proxy.initiate_chat(
    chatbot,
    message=task,
)
