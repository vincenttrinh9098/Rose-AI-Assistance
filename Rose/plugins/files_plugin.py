from plugins.base import Plugin
from commands.files import search_files, open_file
from core.pending_action import set_pending


class FindFilePlugin(Plugin):
    name = "find_file"
    description = "Finds and opens a file on the computer, given a description like 'my resume'."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        results = search_files(query)

        if not results:
            return f"I couldn't find anything matching {query}"
        elif len(results) == 1:
            return open_file(results[0])
        else:
            set_pending("disambiguate_file", matches=results, content=None)
            names = [f"{i+1}. {results[i].split('/')[-1]}" for i in range(min(3, len(results)))]
            return f"I found a few matches: {'. '.join(names)}. Which one, or say the number?"