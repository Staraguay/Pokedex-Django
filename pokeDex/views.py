import time
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as lg
from django.contrib.auth import logout as lo
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import *
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from .utils import cached_data, fetch_all_pokemons
from concurrent.futures import ThreadPoolExecutor
import asyncio
from multiprocessing import Pool

POKE_API_URL = 'https://pokeapi.co/api/v2/pokemon/'

# Vista principal de inicio con todos los pokemons recuperados de la API
class Index(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if cached_data is not None:
            allPokemons = cached_data['results']
            paginate_by = 20
            paginator = Paginator(allPokemons, paginate_by)
            page = self.request.GET.get('page')
            pokemons_on_current_page = paginator.get_page(page)

            start_time = time.time()

            #primera opcion en paralelo 2.5 s usando hilos pero usa mucho procesador
            # pokemons_urls = [pokemon['url'] for pokemon in pokemons_on_current_page]
            # with ThreadPoolExecutor(max_workers=20) as executor:
            #     pokemons = list(executor.map(getOnePokemon, pokemons_urls))

            #Segunda solucion usando programacion asyncrona 0.21 S en promedio usa menos procesador
            pokemons = asyncio.run(fetch_all_pokemons([pokemon['url'] for pokemon in pokemons_on_current_page]))

            #Tercera solucion utilizando multiprocesors 5 s en promedio pero ocupa mucho procesador
            #Usar multiprocessing para ejecutar peticiones en paralelo
            # with Pool(processes=20) as pool:
            #     pokemons = pool.map(getOnePokemon, [pokemon['url'] for pokemon in pokemons_on_current_page])

            end_time = time.time()
            print("Tiempo total en mostrar los pokemon en el inicio")
            print(end_time - start_time)

            context['pagination'] = pokemons_on_current_page
            context['poke_list'] = pokemons
        return context


# Vista que muestra los resultados de la busqueda de un pokemon
class Search(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = self.request.GET.get('pokemon')
        search_term = search_term.replace(' ', '')
        search_term = search_term.lower()
        search_result = [getOnePokemon(POKE_API_URL + search_term)]
        context['search_result'] = search_result

        return context


# Vista que muestra todos los detalles de un pokemon especifico
class Perfil(LoginRequiredMixin, TemplateView):
    template_name = 'pokemons/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_pokemon = getPokemonDetails(self.request.GET.get('id'))
        context['pokemon'] = current_pokemon

        return context


# Vista que dirigue a la pagina acerca de
def about(request):
    return render(request, 'about.html', {})


# funcion para manejar el login de un usuario
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuarios = authenticate(username=username, password=password)

        if usuarios:
            lg(request, usuarios)
            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET['next'])
            return redirect('index')
        else:
            pass

    return render(request, 'login.html', {})


# Funcion para manegar el logout de un usuario
def logout(request):
    lo(request)
    return redirect(login)

