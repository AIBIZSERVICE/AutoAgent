import pytest
from autogen import OpenAIWrapper, config_list_from_json, config_list_openai_aoai
from test_utils import OAI_CONFIG_LIST, KEY_LOC

try:
    from openai import OpenAI
except ImportError:
    skip = True
else:
    skip = False


@pytest.mark.skipif(skip, reason="openai>=1 not installed")
def test_aoai_chat_completion():
    config_list = config_list_from_json(
        env_or_file=OAI_CONFIG_LIST,
        file_location=KEY_LOC,
        filter_dict={"api_type": ["azure"], "model": ["gpt-3.5-turbo"]},
    )
    client = OpenAIWrapper(config_list=config_list)
    # for config in config_list:
    #     print(config)
    #     client = OpenAIWrapper(**config)
    #     response = client.create(messages=[{"role": "user", "content": "2+2="}], cache_seed=None)
    response = client.create(messages=[{"role": "user", "content": "2+2="}], cache_seed=None)
    print(response)
    print(client.extract_text_or_function_call(response))


@pytest.mark.skipif(skip, reason="openai>=1 not installed")
def test_chat_completion():
    config_list = config_list_from_json(
        env_or_file=OAI_CONFIG_LIST,
        file_location=KEY_LOC,
    )
    client = OpenAIWrapper(config_list=config_list)
    response = client.create(messages=[{"role": "user", "content": "1+1="}])
    print(response)
    print(client.extract_text_or_function_call(response))


@pytest.mark.skipif(skip, reason="openai>=1 not installed")
def test_completion():
    config_list = config_list_openai_aoai(KEY_LOC)
    client = OpenAIWrapper(config_list=config_list)
    response = client.create(prompt="1+1=", model="gpt-3.5-turbo-instruct")
    print(response)
    print(client.extract_text_or_function_call(response))


@pytest.mark.skipif(skip, reason="openai>=1 not installed")
@pytest.mark.parametrize(
    "cache_seed, model",
    [
        (None, "gpt-3.5-turbo-instruct"),
        (42, "gpt-3.5-turbo-instruct"),
        (None, "text-ada-001"),
    ],
)
def test_cost(cache_seed, model):
    config_list = config_list_openai_aoai(KEY_LOC)
    client = OpenAIWrapper(config_list=config_list, cache_seed=cache_seed)
    response = client.create(prompt="1+3=", model=model)
    print(response.cost)


@pytest.mark.skipif(skip, reason="openai>=1 not installed")
def test_usage_summary():
    config_list = config_list_openai_aoai(KEY_LOC)
    client = OpenAIWrapper(config_list=config_list)
    response = client.create(prompt="1+3=", model="gpt-3.5-turbo-instruct", cache_seed=42)

    # usage should be recorded
    assert client.actual_usage_summary["total_cost"] > 0, "total_cost should be greater than 0"
    assert client.total_usage_summary["total_cost"] > 0, "total_cost should be greater than 0"

    # check print
    client.print_usage_summary()

    # check update
    client._update_usage_summary(response, use_cache=True)
    assert (
        client.actual_usage_summary["total_cost"] == response.cost * 2
    ), "total_cost should be equal to response.cost * 2"

    # check clear
    client.clear_usage_summary()
    assert client.actual_usage_summary is None, "actual_usage_summary should be None"
    assert client.total_usage_summary is None, "total_usage_summary should be None"

    # actual usage and all usage should be different
    response = client.create(prompt="1+3=", model="gpt-3.5-turbo-instruct", cache_seed=42)
    assert client.total_usage_summary["total_cost"] > 0, "total_cost should be greater than 0"
    assert client.actual_usage_summary is None, "No actual cost should be recorded"


@pytest.mark.skipif(skip, reason="openai>=1 not installed")
def test_create_with_different_models():
    config_list = config_list_from_json(
        env_or_file=OAI_CONFIG_LIST,
        file_location=KEY_LOC,
        filter_dict={"api_type": ["azure"], "model": ["gpt-3.5-turbo", "gpt-4"]},
    )
    messages = [{"role": "user", "content": "2+2="}]

    # create with the same model in config_list
    client = OpenAIWrapper(config_list=config_list)
    response = client.create(messages=messages, model="gpt-3.5-turbo")
    assert response.model in ["gpt-3.5-turbo", "gpt-35-turbo"], "Model not consistent."
    response = client.create(messages=messages, model="gpt-4")
    assert response.model in ["gpt-4", "gpt-4-0613"], "Model not consistent."

    # create with non-existing model in config_list
    try:
        response = client.create(messages=messages, model="gpt-3.5-turbo-16k")
    except ValueError as e:
        print(e)
    else:
        raise ValueError("Expected ValueError")

    # initialize with a specific model
    client = OpenAIWrapper(config_list=config_list, model="gpt-4-1106-preview")
    response = client.create(messages=messages)
    assert response.model in ["gpt-4", "gpt-4-0613"], "Should create with the specified model."
    response = client.create(messages=messages, model="gpt-3.5-turbo")
    assert response.model in ["gpt-3.5-turbo", "gpt-35-turbo"], "Initialized model should be overwritten."

    # initialize with inconsistent models in config_list
    try:
        client = OpenAIWrapper(config_list=config_list, model="gpt-3.5-turbo-16k")
    except ValueError as e:
        print(e)
    else:
        raise ValueError("Expected ValueError")


if __name__ == "__main__":
    test_aoai_chat_completion()
    test_chat_completion()
    test_completion()
    test_cost()
    test_usage_summary()