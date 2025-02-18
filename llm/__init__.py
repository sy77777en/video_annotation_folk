from llm.chatgpt import ChatGPT
from llm.gemini import Gemini
# from llm.deepseek import DeepSeek

ALL_MODELS = {
    "Gemini": ["gemini-2.0-flash-001", "gemini-2.0-flash-lite-preview-02-05", 
            #    "gemini-1.5-flash-001", "gemini-1.5-flash-8b-001", "gemini-1.5-pro-001"
               ],
    "ChatGPT": ["gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18", "o1-2024-12-17"],
}

def get_llm(model="gpt-4o-2024-08-06"):
    if model in ALL_MODELS["ChatGPT"]:
        return ChatGPT(model=model)
    elif model in ALL_MODELS["Gemini"]:
        return Gemini(model=model)
    # elif model == "deepseek":
    #     return DeepSeek()
    else:
        raise ValueError(f"Error: Invalid LLM model '{model}'")
    
def get_all_llms():
    model_names = []
    for model_type, models in ALL_MODELS.items():
        model_names.extend(models)
    return model_names

def get_supported_mode(model="gpt-4o-2024-08-06"):
    if model in ALL_MODELS["ChatGPT"]:
        return ["Image (First-and-Last-Frame)", "Text Only"]
    elif model in ALL_MODELS["Gemini"]:
        return ["Video", "Image (First-and-Last-Frame)", "Text Only"]
    else:
        raise ValueError(f"Error: Invalid LLM model '{model}'")