from typing import Optional


class Token:
    def __init__(self, category: str, lexeme: Optional[str] = None):
        self.category = category
        self.lexeme = lexeme if lexeme is not None else category

    def __repr__(self):
        return "<Token(category='{}', lexeme='{}')>".format(
            self.category, self.lexeme)


class CharacterStream:
    def __init__(self,
                 admissible_characters=None,
                 special_characters=None,
                 escape_character="\\",
                 general_class="char"):
        self._admissible_characters = self._character_set(
            admissible_characters)
        self._special_characters = self._character_set(special_characters)
        self._escape_character = escape_character
        self._general_class = general_class

    @staticmethod
    def _character_set(characters):
        if characters is None:
            return {}
        else:
            return set(char for char in characters)

    def tokenize(self, string):
        tokens = []
        for char in string:
            if char == self._escape_character:
                continue
            if self._admissible_characters and \
                    char not in self._admissible_characters:
                raise ValueError("Unexpected character: %s" % char)
            if char not in self._special_characters:
                tokens.append(Token(category=self._general_class, lexeme=char))
            else:
                tokens.append(Token(category=char))
        return tokens
