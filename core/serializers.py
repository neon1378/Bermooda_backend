from rest_framework import serializers

from .models import *
class ImageSerializer (serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            "id",
            "image_url"
        ]


class CoreSerializer(serializers.ModelSerializer):
    image = ImageSerializer(many=True)

    class Meta:
        model = Core
        fields = [
            "id",
            "image",
    
            "title",
            "description",
            "title_en",
            "description_en"
            
        ]


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = [
            "id",
            "name"
        ]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "id",
            "name"
        ]
