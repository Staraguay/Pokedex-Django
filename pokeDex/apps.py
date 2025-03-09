from django.apps import AppConfig
from .utils import getAllPokemons

class PokedexConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pokeDex'

    def ready(self):
        getAllPokemons()

