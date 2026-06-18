from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from scheduling.models import Course, CourseDifficultyPrediction
from scheduling.ml.predictor import predict_difficulty


@receiver(post_save, sender=Course)
def course_saved_trigger(sender, instance, **kwargs):
    # ensures DB commit before ML runs
    def run_ml():
        label, score = predict_difficulty(instance.title)

        CourseDifficultyPrediction.objects.update_or_create(
            course=instance,
            defaults={
                "predicted_level": label,
                "confidence_score": score,
                "difficulty_score": score,
            }
        )

        Course.objects.filter(pk=instance.pk).update(difficulty_score=score)

    transaction.on_commit(run_ml)