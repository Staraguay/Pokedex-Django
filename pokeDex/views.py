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

POKE_API_URL = 'https://pokeapi.co/api/v2/pokemon/'


# Vista principal de inicio con todos los pokemons recuperados de la API
class Index(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allPokemons = getAllPokemons()
        paginate_by = 20
        paginator = Paginator(allPokemons, paginate_by)
        page = self.request.GET.get('page')
        pokemons_on_current_page = paginator.get_page(page)
        pokemons = [getOnePokemon(pokemon['url']) for pokemon in pokemons_on_current_page]
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

