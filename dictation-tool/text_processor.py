import re


class TextProcessor:
    def __init__(self, config):
        self.config = config

    def process(self, text, language="he"):
        if not text:
            return text
        if self.config.get("remove_filler_words", True):
            text = self._remove_fillers(text, language)
        if self.config.get("use_custom_dictionary", True):
            text = self._apply_dictionary(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _remove_fillers(self, text, language):
        fillers = self.config.get("filler_words", {}).get(language, [])
        if not fillers:
            return text
        fillers_lower = {f.lower() for f in fillers}
        tokens = text.split()
        kept = []
        for token in tokens:
            stripped = token.strip(".,!?;:\"'").lower()
            if stripped not in fillers_lower:
                kept.append(token)
        return " ".join(kept)

    def _apply_dictionary(self, text):
        dictionary = self.config.get("custom_dictionary", {})
        for source, target in dictionary.items():
            text = text.replace(source, target)
        return text
