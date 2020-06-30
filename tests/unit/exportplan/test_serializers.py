from exportplan import serializers


def test_brand_product_details_serializer():

    data = {
        'story': 'Lorem ipsum',
        'location': 'Consectetur adipisicing elit',
        'packaging': 'Dolor sit amet',
        'processes': 'Sed do eiusmod tempor incididunt'
    }

    serializer = serializers.BrandAndProductDetailsSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_brand_product_details_serializer_allows_blank_omitted():

    data = {
        'story': '',
        'location': '',
    }

    serializer = serializers.BrandAndProductDetailsSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_export_plan_serializer_empty_target_markets():

    data = {
        'brand_product_details': {
            'story': '',
            'location': ''
        }
    }

    serializer = serializers.ExportPlanSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_objective_serializer():

    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '2020-03-01',
        'end_date': '2020-12-23',
        'companyexportplan': 1,
        'pk': 2,
    }

    serializer = serializers.ObjectiveSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_new_objective_serializer():

    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '2020-03-01',
        'end_date': '2020-12-23',
        'companyexportplan': 1,
    }

    serializer = serializers.NewObjectiveSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_pk_only_serializer():

    data = {
        'pk': 1
    }

    serializer = serializers.PkOnlySerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data
