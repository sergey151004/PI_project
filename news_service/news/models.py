from django.db import models

class NewsItem(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    source_url = models.URLField()
    source_name = models.CharField(max_length=100)
    published_at = models.DateTimeField(auto_now_add=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title