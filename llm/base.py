class LLM:
    def __init__(self, model):
        pass

    def generate(self, prompt, images=[], video=""):
        raise NotImplementedError

    def generate_batch(self, prompts, images=[], video=[]):
        return [self.generate(prompt, images, video) for prompt in prompts]