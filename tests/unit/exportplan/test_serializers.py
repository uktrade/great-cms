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


def test_objective_serializer_empty_date_fields():

    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '',
        'end_date': '',
        'companyexportplan': 1,
    }

    serializer = serializers.NewObjectiveSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': None,
        'end_date': None,
        'companyexportplan': 1,
    }


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


def target_markets_research_serializer():

    data = {
        'demand': 'Lorem ipsum',
        'competitors': 'Consectetur adipisicing elit',
        'trend': 'Dolor sit amet',
        'unqiue_selling_proposition': 'Sed do eiusmod tempor incididunt',
        'average_price': 10
    }

    serializer = serializers.TargetMarketsResearchSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_population_data_serializer():

    data = {
        'country': 'uk',
        'target_age_groups': ['0-5,5-25'],
    }

    serializer = serializers.PopulationDataSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.data['target_age_groups'] == ['0-5', '5-25']
