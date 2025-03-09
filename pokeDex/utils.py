# Funciones de soporte para obtener los difrentes datos de la API
import time
import requests
import aiohttp
import asyncio

POKE_API_URL = 'https://pokeapi.co/api/v2/pokemon/'
POKE_API_URL_DESCRIPTION = 'https://pokeapi.co/api/v2/pokemon-species/'
POKE_API_URL_ABILITIES = 'https://pokeapi.co/api/v2/ability/'
cached_data = None


async def fetch_url(session, url) -> dict :
    async with session.get(url) as response:
        pokemon_main_data = {}
        response = await response.json()
        if response is not None:
            pokemon_main_data['id'] = response['id']
            pokemon_main_data['name'] = response['name'].capitalize()
            pokemon_main_data['nHabilidades'] = str(len(response['abilities']))
            pokemon_main_data['profileImg'] = response['sprites']['front_default']
        else:
            pokemon_main_data = {}

        return pokemon_main_data

async def fetch_all_pokemons(urls) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)  # Ejecutar todas las solicitudes en paralelo


# Funcion que devuelve un diccionario con los datos de un pokemon en especifico
def getOnePokemon(url: str) -> dict:
    pokemon_main_data = {}
    try:
        response = requests.get(url)
        if response.status_code == 200:
            pokemon_data_all = response.json()
            pokemon_main_data['id'] = pokemon_data_all['id']
            pokemon_main_data['name'] = pokemon_data_all['name'].capitalize()
            pokemon_main_data['nHabilidades'] = str(len(pokemon_data_all['abilities']))
            pokemon_main_data['profileImg'] = pokemon_data_all['sprites']['front_default']
        else:
            pokemon_main_data = {}
    except Exception as e:
        print("Error fetching API data:", e)

    return pokemon_main_data


# Funcion que devuelve los primeros pokemons para ser mostrados en el inicio
def getAllPokemons() -> list:
    global cached_data
    print("Fetching API data at startup... ")
    try:
        response = requests.get(POKE_API_URL + '?limit=10000&offset=0')
        if response.status_code == 200:
            cached_data = response.json()
            print("Fetched API data successfully")
        else:
            cached_data = [{'results': ''}]
    except Exception as e:
        print("Error fetching API data:", e)


# Funcion que duvuelde los detalles y caracteristicas de un pokemon en especifico
def getPokemonDetails(id: str) -> dict:
    pokemon_data_refined = {}

    start_time = time.time()

    try:
        response = requests.get(POKE_API_URL + id)
        if response.status_code == 200:
            pokemon_data = response.json()
            pokemon_data_refined['name'] = pokemon_data['name'].capitalize()
            pokemon_data_refined['nHabilidades'] = str(len(pokemon_data['abilities']))
            pokemon_data_refined['profileImg'] = pokemon_data['sprites']['front_default']
            # se pasa los valores a metros y kg
            pokemon_data_refined['height'] = pokemon_data['height'] / 10
            pokemon_data_refined['weight'] = pokemon_data['weight'] / 10

            response_species = requests.get(POKE_API_URL_DESCRIPTION + id)

            if response_species.status_code == 200:
                descriptions = response_species.json()
                descriptions_list = descriptions['flavor_text_entries']

                # Obtener la descripcion en espanol del pokemon
                for element in descriptions_list:
                    if element['language']['name'] == 'es':
                        pokemon_data_refined['description'] = element['flavor_text']
                        break
                # obtener la categoria del pokemon
                category_list = descriptions['genera']
                for element in category_list:
                    if element['language']['name'] == 'es':
                        pokemon_data_refined['category'] = element['genus']
                        break

                # obtener las habilidades que no esten ocultas y los nombres de manera asyncrona
                abilities_List = pokemon_data['abilities']
                abilities_urls = [element['ability']['url'] for element in abilities_List if element['is_hidden'] == False ]
                pokemon_data_refined['allAbilities'] = asyncio.run(fetch_all_abilities(abilities_urls))

                # obtener el genero del pokemon
                gender = descriptions['gender_rate']
                pokemon_data_refined['gender'] = getGender(gender)

                # obtener el habitad en espaniol 1 llamada de api extra y 0.5 s de tiempo extra
                habitat = descriptions['habitat']['url']
                pokemon_data_refined['habitat'] = getHabitat(habitat)

                #obtener el habitad en ingles directo ahorro de 0.5 s
                #pokemon_data_refined['habitat'] = descriptions['habitat']['name'].capitalize()

                # obtener los tipos de manera asyncrona
                types_list = pokemon_data['types']
                types_url = [element['type']['url'] for element in types_list ]
                pokemon_data_refined['typesNames'] = asyncio.run(fetch_all_types(types_url))

                # Obtener las debilidades de manera asyncrona
                weak_name = asyncio.run(fetch_all_weaknesses(types_url))
                pokemon_data_refined['weakNames'] = list(set(sum(weak_name, [])))

                # obtener estadisticas
                stats_list = pokemon_data['stats']
                pokemon_data_refined['hp'] = stats_list[0]['base_stat']
                pokemon_data_refined['attack'] = stats_list[1]['base_stat']
                pokemon_data_refined['defense'] = stats_list[2]['base_stat']
                pokemon_data_refined['specialAttack'] = stats_list[3]['base_stat']
                pokemon_data_refined['specialDefense'] = stats_list[4]['base_stat']
                pokemon_data_refined['speed'] = stats_list[5]['base_stat']

            else:
                pokemon_data_refined['description'] = 'Descripcion general de Pokemon'



        else:
            pokemon_data_refined = {}
    except Exception as e:
        print("Error fetching API data:", e)

    end_time = time.time()
    print("Tiempo total en obtener los detalles de un pokemon")
    print(end_time - start_time)

    return pokemon_data_refined


# funcion para obtener las habilidades de un pokemon en especifico
async def getAbilities(session, url: str) -> dict:
    async with session.get(url) as response:
        all_abilities = await response.json()
        names_list = all_abilities['names']

        for element in names_list:
            if element['language']['name'] == 'es':
                return element['name']


async def fetch_all_abilities(urls) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [getAbilities(session, url) for url in urls]
        return await asyncio.gather(*tasks)


# funcion para obtener el genero de un pokemon en especifico
def getGender(gender: int) -> int:
    if gender < 0:
        # print('Desconocido')
        return 0

    elif gender == 0:
        # print('Macho')
        return 1

    elif gender > 0 and gender < 8:
        # print('Macho y Hembra')
        return 2

    elif gender == 8:
        # print('Hembra')
        return 3
    else:
        # print('Error')
        return 4


# funcion para obtener el habitat de un pokemon en especifico
def getHabitat(url: str) -> str:
    response = requests.get(url)
    habitat = response.json()
    habitat_list = habitat['names']
    for element in habitat_list:
        if element['language']['name'] == 'es':
            return element['name'].capitalize()


# funcion para obtener los tipos de un pokemon en especifico
async def getTypes(session, url: str) -> str:
    async with session.get(url) as response:
        names_dic = await response.json()
        names_list = names_dic['names']
        for element in names_list:
            if element['language']['name'] == 'es':
                return element['name']

async def fetch_all_types(urls) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [getTypes(session, url) for url in urls]
        return await asyncio.gather(*tasks)


# funcion para obtener las debilidades de un pokemon en especifico
async def getWeaknesses(session, url: str) -> list:
    async with session.get(url) as response:
        weaknesses_dic = await response.json()
        weaknesses_list = weaknesses_dic['damage_relations']['double_damage_from']
        weak_names = [element['name'] for element in weaknesses_list]
        return weak_names

async def fetch_all_weaknesses(urls) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [getWeaknesses(session, url) for url in urls]
        return await asyncio.gather(*tasks)
