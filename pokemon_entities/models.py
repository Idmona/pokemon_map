from django.db import models

class Pokemon(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название (рус.)")
    title_en = models.CharField(max_length=200, blank=True,verbose_name="Название (анг.)")
    title_jp = models.CharField(max_length=200, blank=True, verbose_name="Название (яп.)")
    image = models.ImageField(null=True, blank=True, upload_to="pokemon_images", verbose_name="Изображение")
    description = models.TextField(blank=True, verbose_name="Описание")
    previous_evolution = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='next_evolutions',
        verbose_name="Эволюционировал из"
    )

    def __str__(self):
        return '{}'.format(self.title)

class PokemonEntity(models.Model):
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, verbose_name="Покемон", related_name="pokemon_entity")
    appeared_at = models.DateTimeField(null=True, blank=True, verbose_name="Время появления")
    disappeared_at = models.DateTimeField(null=True, blank=True, verbose_name="Время исчезновения")
    level = models.IntegerField(null=True, blank=True, verbose_name="Уровень")
    health_points = models.IntegerField(null=True, blank=True, verbose_name="Здоровье")
    damage = models.IntegerField(null=True, blank=True, verbose_name="Атака")
    defense = models.IntegerField(null=True, blank=True, verbose_name="Защита")
    stamina = models.IntegerField(null=True, blank=True, verbose_name="Выносливость")