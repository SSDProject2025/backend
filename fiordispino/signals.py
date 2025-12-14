from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count

from .models import Game, GamePlayed


def _update_game_stats(game_instance):

    stats = game_instance.played_by_user.aggregate(
        average=Avg('rating'),
        count=Count('id')
    )

    game_instance.global_rating = stats['average'] or 0.0
    game_instance.rating_count = stats['count'] or 0

    game_instance.save(update_fields=['global_rating', 'rating_count'])


@receiver(post_save, sender=GamePlayed)
def update_stats_on_save(sender, instance, created, **kwargs):
    # this method runs whenever a user set a game as played or edit the rating
    _update_game_stats(instance.game)


@receiver(post_delete, sender=GamePlayed)
def update_stats_on_delete(sender, instance, **kwargs):
    _update_game_stats(instance.game)