from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import WorkSpace

class WorkSpaceSerializer(ModelSerializer):
    class Meta:
        model =WorkSpace
        fields =[
            "id",

            "business_type",

            "reference_sub_category",
            "reference_category",
            "jadoo_brand_name",
            "business_detail",
            "city",
            "state",
            "state_name",
            "city_name",
            "main_category_data",
            "sub_category_data"
        ]
    def update(self,instance,validated_data):
        
        jadoo_brand_name= validated_data.get("jadoo_brand_name",None)
        if jadoo_brand_name == None:
            raise serializers.ValidationError({"error":{
                "detail":"نام پروفایل اجباری میباشد"
            }})
        if WorkSpace.objects.filter(jadoo_brand_name=jadoo_brand_name).exists():
            if instance.jadoo_brand_name != jadoo_brand_name:
                raise serializers.ValidationError({"error":{
                "detail":"نام پروفایل انتخاب شده درحال حاضر وجود دارد"
                }})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
