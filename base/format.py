from collections import OrderedDict


def sub_format(data):
    return {
        "id": data.id,
        "name": data.name
    }

def user_format(data):
    return OrderedDict([
        ("id", data.id),
        ("name", data.name),
        ("mobile", data.mobile)
    ])

def category_format(data):
    return OrderedDict([
        ('id', data.id),
        ('content', data.content),
        ('slug', data.slug),
    ])


def product_format(data):
    return OrderedDict([
        ("id", data.id),
        ("name", data.name),
        ("tag", data.tag),
        ("pesonType", data.pesonType),
        ("level", data.level),
        ("price", data.price),
        ("price_type", data.price_type),
        ("ctg_slug", None if not data.category.slug else data.category.slug),
        ('category', None if not data.category else category_format(data.category)),
    ])
