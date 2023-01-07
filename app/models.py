from django.db import models

from modu_property.common.models.models import DateTimeFields


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()


class News(DateTimeFields):
    title = models.CharField(max_length=100, help_text="기사 제목")
    body = models.TextField(help_text="기사 본문")
    published_date = models.DateTimeField(help_text="기사 게시일")
    link = models.URLField(help_text="네이버 뉴스 플랫폼의 기사 링크")
