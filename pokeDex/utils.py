# Funciones de soporte para obtener los difrentes datos de la API
import requests

POKE_API_URL = 'https://pokeapi.co/api/v2/pokemon/'
POKE_API_URL_DESCRIPTION = 'https://pokeapi.co/api/v2/pokemon-species/'
POKE_API_URL_ABILITIES = 'https://pokeapi.co/api/v2/ability/'


# Funcion que devuelve un diccionario con los datos de un pokemon en especifico
def getOnePokemon(url: str) -> dict:
    response = requests.get(url)
    if response.status_code == 200:
        pokemon_data_all = response.json()
        pokemon_data_all['name'] = pokemon_data_all['name'].capitalize()
        pokemon_data_all['nHabilidades'] = str(len(pokemon_data_all['abilities']))
        pokemon_data_all['profileImg'] = pokemon_data_all['sprites']['front_default']
    else:
        pokemon_data_all = {}

    return pokemon_data_all


# Funcion que devuelve todos los pokemons para ser mostrados en el inicio
def getAllPokemons() -> list:
    response = requests.get(POKE_API_URL + '?limit=100000&offset=0')
    if response.status_code == 200:
        all_pokemons = response.json()
    else:
        all_pokemons = [{'results': ''}]

    return all_pokemons['results']


# Funcion que duvuelde los detalles y caracteristicas de un pokemon en especifico
def getPokemonDetails(id: str) -> dict:
    response = requests.get(POKE_API_URL + id)

    if response.status_code == 200:
        pokemon_data = response.json()
        pokemon_data['name'] = pokemon_data['name'].capitalize()
        pokemon_data['nHabilidades'] = str(len(pokemon_data['abilities']))
        pokemon_data['profileImg'] = pokemon_data['sprites']['front_default']

        # se pasa los valores a metros y kg
        height = pokemon_data['height'] / 10
        weight = pokemon_data['weight'] / 10
        pokemon_data['height'] = height
        pokemon_data['weight'] = weight

        response_species = requests.get(POKE_API_URL_DESCRIPTION + id)

        if response_species.status_code == 200:
            descriptions = response_species.json()
            descriptions_list = descriptions['flavor_text_entries']

            # Obtener la descripcion en espanol del pokemon
            for element in descriptions_list:
                if element['language']['name'] == 'es':
                    pokemon_data['description'] = element['flavor_text']
                    break
            # obtener la categoria del pokemon
            category_list = descriptions['genera']
            for element in category_list:
                if element['language']['name'] == 'es':
                    pokemon_data['category'] = element['genus']
                    break

            # obtener las habilidades que no esten ocultas
            abilities_List = pokemon_data['abilities']
            abilities_name = []
            for element in abilities_List:
                if element['is_hidden'] == False:
                    abilities_name.append(getAbilities(element['ability']['url']))

            pokemon_data['allAbilities'] = abilities_name

            # obtener el genero del pokemon
            gender = descriptions['gender_rate']
            pokemon_data['gender'] = getGender(gender)

            # obtener el habitad
            habitat = descriptions['habitat']['url']
            pokemon_data['habitat'] = getHabitat(habitat)

            # obtener los tipos
            types_name = []
            types_list = pokemon_data['types']
            for element in types_list:
                types_name.append(getTypes(element['type']['url']))
            pokemon_data['typesNames'] = types_name

            # Obtener las debilidades
            weak_name = []
            weaknesses_list = types_list
            for element in weaknesses_list:
                weak_name += getWeaknesses(element['type']['url'])
            pokemon_data['weakNames'] = list(set(weak_name))

            # obtener estadisticas
            stats_list = pokemon_data['stats']
            pokemon_data['hp'] = stats_list[0]['base_stat']
            pokemon_data['attack'] = stats_list[1]['base_stat']
            pokemon_data['defense'] = stats_list[2]['base_stat']
            pokemon_data['specialAttack'] = stats_list[3]['base_stat']
            pokemon_data['specialDefense'] = stats_list[4]['base_stat']
            pokemon_data['speed'] = stats_list[5]['base_stat']

        else:
            pokemon_data['description'] = 'Descripcion general de Pokemon'



    else:
        pokemon_data = {}

    return pokemon_data


# funcion para obtener las habilidades de un pokemon en especifico
def getAbilities(url: str) -> dict:
    response = requests.get(url)
    all_abilities = response.json()
    names_list = all_abilities['names']

    for element in names_list:
        if element['language']['name'] == 'es':
            return element['name']


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
def getTypes(url: str) -> str:
    response = requests.get(url)
    names_dic = response.json()
    names_list = names_dic['names']

    for element in names_list:
        if element['language']['name'] == 'es':
            return element['name']


# funcion para obtener las debilidades de un pokemon en especifico
def getWeaknesses(url: str) -> list:
    response = requests.get(url)
    weaknesses_dic = response.json()
    weaknesses_list = weaknesses_dic['damage_relations']['double_damage_from']
    weak_names = []

    for element in weaknesses_list:
        weak_names.append(getTypes(element['url']))

    return weak_names
