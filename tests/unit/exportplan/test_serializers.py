from exportplan import serializers


def test_brand_product_details_serializer():

    data = {
        'story': 'Lorem ipsum',
        'location': 'Consectetur adipisicing elit',
        'packaging': 'Dolor sit amet',
        'processes': 'Sed do eiusmod tempor incididunt'
    }

    serializer = serializers.BrandAndProductDetailsSerializer(data)

    assert serializer.data == data


def test_brand_product_details_serializer_allows_blank_omitted():

    data = {
        'story': '',
        'location': '',
    }

    serializer = serializers.BrandAndProductDetailsSerializer(data)

    assert serializer.data == data


def test_export_plan_serializer_empty_target_markets():

    data = {
        'brand_product_details': {
            'story': '',
            'location': ''
        }
    }

    serializer = serializers.ExportPlanSerializer(data)

    assert serializer.data == data
