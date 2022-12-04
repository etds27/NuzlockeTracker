from PokemonGameDataAdapter import PokemonGameDataAdapter

class RandomizedOutputFileAdapter(PokemonGameDataAdapter):
    def __init__(self, *args, **kwargs):
        super(RandomizedOutputFileAdapter, self).__init__(*args, **kwargs)