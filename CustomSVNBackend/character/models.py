import os

from django.db import models
from django.conf import settings

from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Gender(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class Race(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class ItemAttribute(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Character(models.Model):
    # 保留原有的字段
    name = models.CharField(max_length=100)
    character_id = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT, blank=True, null=True)
    race = models.ForeignKey(Race, on_delete=models.PROTECT, blank=True, null=True)

    # 新增字段
    tags = models.ManyToManyField(Tag, related_name='characters', blank=True, )
    items = models.ManyToManyField(Item, through='CharacterItem', related_name='characters', blank=True, )

    class Meta:
        unique_together = ['character_id', 'name']
        ordering = ['id']

    def __str__(self):
        return self.name


class CharacterItem(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    attributes = models.ManyToManyField(ItemAttribute, through='CharacterItemAttribute')

    class Meta:
        unique_together = ['character', 'item']

    def __str__(self):
        return f"{self.character.name}'s {self.item.name}"


class CharacterItemAttribute(models.Model):
    character_item = models.ForeignKey(CharacterItem, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ItemAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    class Meta:
        unique_together = ['character_item', 'attribute']

    def __str__(self):
        return f"{self.character_item}: {self.attribute.name} = {self.value}"


class Thumbnail(models.Model):
    character = models.ForeignKey(Character, related_name='thumbnails', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='character_thumbnails/')

    def __str__(self):
        return f"Thumbnail for {self.character.name}"

    def delete(self, *args, **kwargs):
        # 存储文件路径
        storage, path = self.image.storage, self.image.path
        # 删除数据库中的记录
        super(Thumbnail, self).delete(*args, **kwargs)
        # 删除文件系统中的文件
        storage.delete(path)

    def save(self, *args, **kwargs):
        if self.character.thumbnails.count() >= settings.MAX_THUMBNAILS_PER_CHARACTER:
            raise ValueError("Maximum number of thumbnails reached for this character")
        super().save(*args, **kwargs)


@receiver(pre_delete, sender=Thumbnail)
def thumbnail_delete(sender, instance, **kwargs):
    # 在删除Thumbnail对象之前，如果存在图片文件，则删除它
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
