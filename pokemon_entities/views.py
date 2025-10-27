import folium


from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.timezone import localtime
from django.db.models import Q

from pokemon_entities.models import Pokemon, PokemonEntity

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    current_time = localtime()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    active_entities = PokemonEntity.objects.filter(
        Q(appeared_at__lte=current_time) | Q(appeared_at__isnull=True),
        Q(disappeared_at__gte=current_time) | Q(disappeared_at__isnull=True),
    ).select_related('pokemon')

    for entity in active_entities:
        if entity.pokemon.image:
            image_url = request.build_absolute_uri(entity.pokemon.image.url)
        else:
            image_url = DEFAULT_IMAGE_URL

        add_pokemon(
            folium_map,
            entity.latitude,
            entity.longitude,
            image_url
        )

    pokemons_on_page = []
    for pokemon in Pokemon.objects.all():
        if pokemon.image:
            img_url = request.build_absolute_uri(pokemon.image.url)
        else:
            img_url = DEFAULT_IMAGE_URL

        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': img_url,
            'title': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound("<h1>Pokemon not found</h1>")

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    current_time = localtime()

    entities = pokemon.pokemon_entity.filter(
        (Q(appeared_at__lte=current_time) | Q(appeared_at__isnull=True)) &
        (Q(disappeared_at__gte=current_time) | Q(disappeared_at__isnull=True))
    )

    for entity in entities:
        image_url = request.build_absolute_uri(pokemon.image.url) if pokemon.image else DEFAULT_IMAGE_URL
        add_pokemon(folium_map, entity.latitude, entity.longitude, image_url)

    pokemon_data = {
        'pokemon_id': pokemon.id,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else DEFAULT_IMAGE_URL,
        'description': pokemon.description,
        'entities': [
            {
                'latitude': entity.latitude,
                'longitude': entity.longitude,
                'level': entity.level,
                'health_points': entity.health_points,
                'damage': entity.damage,
                'defense': entity.defense,
                'stamina': entity.stamina,
            } for entity in entities
        ]
    }
    if pokemon.previous_evolution:
        prev = pokemon.previous_evolution
        pokemon_data['previous_evolution'] = {
            'pokemon_id': prev.id,
            'title_ru': prev.title,
            'img_url' : request.build_absolute_uri(prev.image.url) if prev.image else DEFAULT_IMAGE_URL
        }

    next_evolution = pokemon.next_evolutions.first()  # Берём первого потомка
    if next_evolution:
        pokemon_data['next_evolution'] = {
            'pokemon_id': next_evolution.id,
            'title_ru': next_evolution.title,
            'img_url': request.build_absolute_uri(
                next_evolution.image.url) if next_evolution.image else DEFAULT_IMAGE_URL
        }

    return render(request,'pokemon.html',context={
            'map': folium_map._repr_html_(),
            'pokemon': pokemon_data
    })