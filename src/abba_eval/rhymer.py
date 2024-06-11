from pydantic import BaseModel, Field, model_validator
import instructor
from litellm import completion

from typing_extensions import Self


class RhymeCheckResponse(BaseModel):
    word1: str = Field(..., description="The first word checked")
    word2: str = Field(..., description="The second word checked")
    word1_phonetic_spelling: str = Field(
        ..., description="Phonetic spelling of the first word"
    )
    word2_phonetic_spelling: str = Field(
        ..., description="Phonetic spelling of the second word"
    )
    conclusion: bool = Field(..., description="Do the words rhyme? Near rhymes or phonetic rhymes are allowed.")
    explanation: str = Field(
        ..., description="Explanation of the rhyme check conclusion"
    )


class ABBAPoem(BaseModel):
    rhyme_word_A1: str = Field(description="The word that sentence A1 ends with.")
    sentence_A1: str = Field(
        description="The sentence that ends with the rhyme word A1."
    )
    rhyme_word_B1: str = Field(
        description="The word that sentence B1 ends with. It SHOULD NOT rhyme with rhyme_word_A1."
    )
    sentence_B1: str = Field(
        description="The sentence that ends with the rhyme word B1."
    )
    rhyme_word_B2: str = Field(
        description="The word that sentence B2 ends with. It SHOULD rhyme with rhyme_word_B1. It SHOULD NOT rhyme with rhyme_word_A1."
    )
    sentence_B2: str = Field(
        description="The sentence that ends with the rhyme word B2."
    )
    rhyme_word_A2: str = Field(
        description="The word that sentence A2 ends with. It SHOULD rhyme with rhyme_word_A1. It SHOULD NOT rhyme with rhyme_word_B2."
    )
    sentence_A2: str = Field(
        description="The sentence that ends with the rhyme word A2."
    )

    @model_validator(mode="after")
    def check_rhyme_words_used(self) -> Self:
        if (
            self.rhyme_word_A1.lower() in self.sentence_A1.split(" ")[-1].lower()
            and self.rhyme_word_B1.lower() in self.sentence_B1.split(" ")[-1].lower()
            and self.rhyme_word_B2.lower() in self.sentence_B2.split(" ")[-1].lower()
            and self.rhyme_word_A2.lower() in self.sentence_A2.split(" ")[-1].lower()
        ):
            return self
        else:
            raise ValueError(
                f"at least one sentence doesnt end with the correct rhyme word. \n\n {self}"
            )

    @model_validator(mode="after")
    def check_abba(self) -> Self:
        if not check_rhyme(self.rhyme_word_A1, self.rhyme_word_A2).conclusion:
            raise ValueError(
                f"Rhyme words A1 and A2 do not rhyme: {self.rhyme_word_A1} {self.rhyme_word_A2}"
            )
        if not check_rhyme(self.rhyme_word_B1, self.rhyme_word_B2).conclusion:
            raise ValueError(
                f"Rhyme words B1 and B2 do not rhyme: {self.rhyme_word_B1} {self.rhyme_word_B2}"
            )
        if check_rhyme(self.rhyme_word_A1, self.rhyme_word_B1).conclusion:
            raise ValueError(
                f"Rhyme words A1 and B1 rhyme: {self.rhyme_word_A1} {self.rhyme_word_B1}"
            )
        return self

def check_rhyme(word1: str, word2: str) -> RhymeCheckResponse:
    client = instructor.from_litellm(completion)
    return client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        messages=[
            {
                "content": f"Check if the following two words rhyme:{word1} {word2}. First spell the words phonetically. Then determine if the words rhyme. Finally provide an explanation of your conclusion. You may allow imperfect rhymes.",
                "role": "user",
            }
        ],
        response_model=RhymeCheckResponse,
    )


def create_poem(topic: str) -> ABBAPoem:
    client = instructor.from_litellm(completion)
    return client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        messages=[
            {
                "content": f"Create a 4 line poem in ABBA rhyme scheme about the following topic: {topic}. Return only the poem.",
                "role": "user",
            }
        ],
        response_model=ABBAPoem,
    )

def parse_poem(poem: str) -> ABBAPoem:
    lines = [line.strip() for line in poem.strip().split("\n")]
    assert len(lines) == 4
    return ABBAPoem(
        rhyme_word_A1="".join(c for c in lines[0].split(" ")[-1] if c.isalpha()),
        sentence_A1=lines[0],
        rhyme_word_B1="".join(c for c in lines[1].split(" ")[-1] if c.isalpha()),
        sentence_B1=lines[1],
        rhyme_word_B2="".join(c for c in lines[2].split(" ")[-1] if c.isalpha()),
        sentence_B2=lines[2],
        rhyme_word_A2="".join(c for c in lines[3].split(" ")[-1] if c.isalpha()),
        sentence_A2=lines[3],
    )

def create_n_poems(topic: str, n:int) -> ABBAPoem:
    prompt = f"""You are helping me create 4 line poems in ABBA schema.
Do not return (A) / (B) indicators.
The A lines must not rhyme with the B lines.
You may allow imperfect / near rhyme as long as it sounds almost the same.
Create {n} poems each split by ---
The topic of the poem should be: {topic}"""
    output = completion(
        model="gpt-4o-2024-05-13",
        messages=[
            {
                "content": prompt,
                "role": "user",
            }
        ],
    )['choices'][0]['message']['content']

    return output.split('\n---\n')
    

if __name__ == "__main__":
    print("---".join(create_n_poems("bad ukulele playing",3)))