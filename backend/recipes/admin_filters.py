from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Avg, Subquery
from .models import Recipe


class HasRecipesFilter(SimpleListFilter):
    title = 'Наличие в рецептах'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Есть в рецептах'),
            ('no', 'Нет в рецептах'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(recipes_count=Count('recipes'))
        if self.value() == 'yes':
            return queryset.filter(recipes_count__gt=0)
        if self.value() == 'no':
            return queryset.filter(recipes_count=0)
        return queryset


class CookingTimeFilter(SimpleListFilter):
    """Интеллектуальный фильтр по времени готовки с автоматическими порогами"""
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        # Получаем статистику по текущим рецептам
        stats = Recipe.objects.aggregate(
            avg_time=Avg('cooking_time'),
            median_time=Subquery(
                Recipe.objects.order_by('cooking_time').values('cooking_time')[
                    int(Recipe.objects.count() / 2)
                ][:1]
            )
        )
        
        # Автоматические пороги на основе статистики
        fast_threshold = int(stats['median_time'] * 0.7)
        medium_threshold = int(stats['median_time'] * 1.5)
        
        # Подсчет количества в каждой группе
        counts = {
            'fast': Recipe.objects.filter(
                cooking_time__lte=fast_threshold).count(),
            'medium': Recipe.objects.filter(
                cooking_time__gt=fast_threshold, 
                cooking_time__lte=medium_threshold
            ).count(),
            'slow': Recipe.objects.filter(
                cooking_time__gt=medium_threshold).count()
        }
        
        return (
            ('fast', f'Быстрые (до {fast_threshold} мин) ({counts["fast"]})'),
            (
                'medium',
                f'Средние ({fast_threshold}-{medium_threshold} мин) ({counts["medium"]})'
            ),
            ('slow',
             f'Долгие (более {medium_threshold} мин) ({counts["slow"]})'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return queryset.filter(cooking_time__lte=30)
        if self.value() == 'medium':
            return queryset.filter(cooking_time__gt=30, cooking_time__lte=60)
        if self.value() == 'slow':
            return queryset.filter(cooking_time__gt=60)
        return queryset 
    