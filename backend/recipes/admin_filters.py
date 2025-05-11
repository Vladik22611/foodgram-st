from django.contrib.admin import SimpleListFilter
from django.db.models import Count


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
    """
    Фильтр по времени готовки с фиксированными порогами
    """
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    FAST_THRESHOLD = 30
    MEDIUM_THRESHOLD = 60

    def lookups(self, request, model_admin):
        # Сохраняем model_admin для использования в queryset
        self.model_admin = model_admin

        # Получаем базовый queryset
        base_qs = model_admin.get_queryset(request)

        # Считаем количество для каждой категории
        counts = {
            'fast': base_qs.filter(
                cooking_time__lte=self.FAST_THRESHOLD).count(),
            'medium': base_qs.filter(
                cooking_time__gt=self.FAST_THRESHOLD,
                cooking_time__lte=self.MEDIUM_THRESHOLD
            ).count(),
            'slow': base_qs.filter(
                cooking_time__gt=self.MEDIUM_THRESHOLD).count()
        }

        return (
            ('fast',
             f'Быстрые (до {self.FAST_THRESHOLD} мин) ({counts["fast"]})'),
            ('medium', f'Средние ({self.FAST_THRESHOLD}-{self.MEDIUM_THRESHOLD} мин) ({counts["medium"]})'),
            ('slow',
             f'Долгие (более {self.MEDIUM_THRESHOLD} мин) ({counts["slow"]})'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return queryset.filter(cooking_time__lte=self.FAST_THRESHOLD)
        if self.value() == 'medium':
            return queryset.filter(
                cooking_time__gt=self.FAST_THRESHOLD,
                cooking_time__lte=self.MEDIUM_THRESHOLD
            )
        if self.value() == 'slow':
            return queryset.filter(cooking_time__gt=self.MEDIUM_THRESHOLD)
        return queryset
