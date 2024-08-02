import click
from dataclasses import dataclass


@dataclass
class PromptItem():
    prompt: str
    confirmed: bool = True

    def __init__(self, prompt: str, confirmed=True):
        self.prompt = prompt
        self.confirmed = confirmed

    def is_confirmed(self) -> bool:
        return self.confirmed

    def __str__(self) -> str:
        return self.prompt


class MultiLinePromt():

    end_token: str = "!end"

    @classmethod
    def get_prompt(cls) -> str:
        accomulated_prompts = []
        click.echo(
            "Entering multiline prompt, please end the conversation "
            f"with '{cls.end_token}' to continue")
        while True:
            prompt = click.prompt("", prompt_suffix="> ")
            if prompt.strip() == cls.end_token:
                break
            else:
                accomulated_prompts.append(f"{prompt}\n")

        return "".join(accomulated_prompts)

    @classmethod
    def get_prompt_with_confirmation(cls) -> PromptItem:
        prompt = cls.get_prompt()
        result = click.confirm(f'Is this the correct input: \n{prompt}\n')
        return PromptItem(prompt, result)

    @classmethod
    def get_and_wait_prompt(cls) -> PromptItem:
        result = PromptItem("")
        while True:
            result = cls.get_prompt_with_confirmation()
            if result.is_confirmed():
                break
        return result
