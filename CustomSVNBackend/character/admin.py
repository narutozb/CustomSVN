from django.contrib import admin
from django.utils.html import format_html
from .models import Gender, Race, Tag, Item, ItemAttribute, Character, CharacterItem, CharacterItemAttribute, Thumbnail


class TrackedModelAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not change:  # 如果是创建新对象
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑现有对象
            return self.readonly_fields
        return ('created_at', 'updated_at')  # 创建新对象时


@admin.register(Gender)
class GenderAdmin(TrackedModelAdmin):
    list_display = ('name', 'description', 'created_at', 'created_by', 'updated_at', 'updated_by')
    search_fields = ('name', 'description')


@admin.register(Race)
class RaceAdmin(TrackedModelAdmin):
    list_display = ('name', 'description', 'created_at', 'created_by', 'updated_at', 'updated_by')
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(TrackedModelAdmin):
    list_display = ('name', 'description', 'active', 'created_at', 'created_by', 'updated_at', 'updated_by')
    search_fields = ('name', 'description')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(ItemAttribute)
class ItemAttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class CharacterItemInline(admin.TabularInline):
    model = CharacterItem
    extra = 1


class CharacterItemAttributeInline(admin.TabularInline):
    model = CharacterItemAttribute
    extra = 1


@admin.register(CharacterItem)
class CharacterItemAdmin(admin.ModelAdmin):
    list_display = ('character', 'item')
    list_filter = ('character', 'item')
    search_fields = ('character__name', 'item__name')
    inlines = [CharacterItemAttributeInline]


@admin.register(CharacterItemAttribute)
class CharacterItemAttributeAdmin(admin.ModelAdmin):
    list_display = ('character_item', 'attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('character_item__character__name', 'character_item__item__name', 'attribute__name', 'value')


class ThumbnailInline(admin.TabularInline):
    model = Thumbnail
    extra = 1


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'character_id', 'gender', 'race', 'height', 'tag_list', 'thumbnail_preview')
    list_filter = ('gender', 'race', 'tags')
    search_fields = ('name', 'character_id', 'description')
    filter_horizontal = ('tags',)
    inlines = [ThumbnailInline, CharacterItemInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'character_id', 'description', 'height')
        }),
        ('Characteristics', {
            'fields': ('gender', 'race', 'tags')
        }),
        ('Items', {
            'fields': ('get_items',),
        }),
    )
    readonly_fields = ('get_items',)

    def tag_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    tag_list.short_description = 'Tags'

    def thumbnail_preview(self, obj):
        thumbnail = obj.thumbnails.first()
        if thumbnail:
            return format_html('<img src="{}" width="50" height="50" />', thumbnail.image.url)
        return "No thumbnail"

    thumbnail_preview.short_description = 'Thumbnail'

    def get_items(self, obj):
        items_html = []
        for character_item in obj.characteritem_set.all():
            item_html = f"<strong>{character_item.item.name}</strong>:<br>"
            attributes = character_item.attributes.all()
            for attr in attributes:
                value = CharacterItemAttribute.objects.get(character_item=character_item, attribute=attr).value
                item_html += f"- {attr.name}: {value}<br>"
            items_html.append(item_html)
        return format_html("<br>".join(items_html))

    get_items.short_description = 'Character Items'

    class Media:
        css = {
            'all': ('admin/css/character_admin.css',)
        }


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ('character', 'image_preview')
    search_fields = ('character__name',)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.image.url)

    image_preview.short_description = 'Image'
