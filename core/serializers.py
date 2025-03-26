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


class MainFileSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    class Meta:
        model = MainFile
        fields = [
            "id",
            "file_url",
            "file_name"
        ]
    def get_file_name(self, obj):
        return os.path.basename(obj.file.name) if obj.file else None



class AppUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "last_version",
            "is_force",
            "cafe_bazar_link",
            "myket_link",
            "download_link",
        ]




