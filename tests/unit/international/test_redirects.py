import pytest


@pytest.mark.parametrize(
    'previous_url,migrated_url',
    (
        ('/investment-support-directory/', '/international/investment-support-directory/'),
        ('/international/trade/search/', '/international/buy-from-the-uk/find-a-supplier/'),
        ('/international/trade/', '/international/buy-from-the-uk/'),
        ('/international/content/trade/how-we-help-you-buy/', '/international/buy-from-the-uk/'),
        (
            '/international/content/investment/why-invest-in-the-uk/uk-investment-zones/',
            '/international/investment/uk-investment-zones/',
        ),
        (
            '/international/content/investment/how-we-can-help/uk-tax-and-incentives/',
            '/international/investment/uk-tax-and-incentives/',
        ),
        (
            '/international/content/investment/why-invest-in-the-uk/uk-talent-and-labour/',
            '/international/investment/uk-talent-and-labour/',
        ),
        (
            '/international/content/investment/why-invest-in-the-uk/uk-innovation/',
            '/international/investment/uk-innovation/',
        ),
        (
            '/international/content/investment/why-invest-in-the-uk/uk-infrastructure/',
            '/international/investment/uk-infrastructure/',
        ),
        (
            '/international/content/investment/why-invest-in-the-uk/clean-growth-in-the-uk/',
            '/international/investment/clean-growth-in-the-uk/',
        ),
        (
            '/international/content/investment/how-we-can-help/freeports-in-the-uk/',
            '/international/investment/freeports-in-the-uk/',
        ),
        ('/international/content/investment/regions/', '/international/investment/regions/'),
        ('/international/content/investment/regions/wales/', '/international/investment/regions/wales/'),
        (
            '/international/content/investment/regions/south-england/',
            '/international/investment/regions/south-england/',
        ),
        (
            '/international/content/investment/regions/northern-ireland/',
            '/international/investment/regions/northern-ireland/',
        ),
        (
            '/international/content/investment/regions/north-england/',
            '/international/investment/regions/north-england/',
        ),
        ('/international/content/investment/regions/midlands/', '/international/investment/regions/midlands/'),
        ('/international/content/investment/regions/scotland/', '/international/investment/regions/scotland/'),
        ('/international/content/investment/sectors/', '/international/investment/sectors/'),
        (
            '/international/content/investment/sectors/aerospace-and-jet-zero/',
            '/international/investment/sectors/aerospace-and-jet-zero/',
        ),
        (
            '/international/content/investment/sectors/biopharmaceuticals/',
            '/international/investment/sectors/biopharmaceuticals/',
        ),
        (
            '/international/content/investment/sectors/carbon-capture-usage-and-storage/',
            '/international/investment/sectors/carbon-capture-usage-and-storage/',
        ),
        ('/international/content/investment/sectors/chemicals/', '/international/investment/sectors/chemicals/'),
        (
            '/international/content/investment/sectors/civil-nuclear/',
            '/international/investment/sectors/civil-nuclear/',
        ),
        ('/international/content/investment/sectors/agri-tech/', '/international/investment/sectors/agri-tech/'),
        (
            '/international/content/investment/sectors/creative-industries/',
            '/international/investment/sectors/creative-industries/',
        ),
        (
            '/international/content/investment/sectors/cyber-security/',
            '/international/investment/sectors/cyber-security/',
        ),
        ('/international/content/investment/sectors/edtech/', '/international/investment/sectors/edtech/'),
        (
            '/international/content/investment/sectors/financial-services/',
            '/international/investment/sectors/financial-services/',
        ),
        ('/international/content/investment/sectors/fintech/', '/international/investment/sectors/fintech/'),
        (
            '/international/content/investment/sectors/food-and-drink/',
            '/international/investment/sectors/food-and-drink/',
        ),
        (
            '/international/content/investment/sectors/precision-medicine/',
            '/international/investment/sectors/precision-medicine/',
        ),
        (
            '/international/content/investment/sectors/green-shipping/',
            '/international/investment/sectors/green-shipping/',
        ),
        (
            '/international/content/investment/sectors/green-finance/',
            '/international/investment/sectors/green-finance/',
        ),
        (
            '/international/content/investment/sectors/greener-buildings/',
            '/international/investment/sectors/greener-buildings/',
        ),
        (
            '/international/content/investment/sectors/healthcare-and-life-sciences/',
            '/international/investment/sectors/healthcare-and-life-sciences/',
        ),
        ('/international/content/investment/sectors/hydrogen/', '/international/investment/sectors/hydrogen/'),
        ('/international/content/investment/sectors/medtech/', '/international/investment/sectors/medtech/'),
        (
            '/international/content/investment/sectors/mineral-extraction-and-refining/',
            '/international/investment/sectors/mineral-extraction-and-refining/',
        ),
        (
            '/international/content/investment/sectors/offshore-wind/',
            '/international/investment/sectors/offshore-wind/',
        ),
        (
            '/international/content/investment/sectors/professional-and-business-services/',
            '/international/investment/sectors/professional-and-business-services/',
        ),
        ('/international/content/investment/sectors/real-estate/', '/international/investment/sectors/real-estate/'),
        ('/international/content/investment/sectors/retail/', '/international/investment/sectors/retail/'),
        ('/international/content/investment/sectors/space/', '/international/investment/sectors/space/'),
        (
            '/international/content/investment/sectors/sports-economy/',
            '/international/investment/sectors/sports-economy/',
        ),
        (
            '/international/content/investment/sectors/sustainable-infrastructure/',
            '/international/investment/sectors/sustainable-infrastructure/',
        ),
        ('/international/content/investment/sectors/technology/', '/international/investment/sectors/technology/'),
        ('/international/content/investment/sectors/oil-and-gas/', '/international/investment/sectors/oil-and-gas/'),
        (
            '/international/content/investment/sectors/zero-emission-vehicles/',
            '/international/investment/sectors/zero-emission-vehicles/',
        ),
        (
            '/international/content/investment/opportunities/accelerated-electrification-transition-in-the-north-east-of-england/',  # noqa:E501
            '/international/investment/accelerated-electrification-transition-in-the-north-east-of-england/',
        ),
        (
            '/international/content/investment/opportunities/5g-and-digitisation-in-norfolk-and-suffolk-east-of-england/',  # noqa:E501
            '/international/investment/5g-and-digitisation-in-norfolk-and-suffolk-east-of-england/',
        ),
        (
            '/international/content/investment/opportunities/biomanufacturing-in-tees-valley/',
            '/international/investment/biomanufacturing-in-tees-valley/',
        ),
        (
            '/international/content/investment/opportunities/cam-modelling-and-simulation-in-oxfordshire/',
            '/international/investment/cam-modelling-and-simulation-in-oxfordshire/',
        ),
        (
            '/international/content/investment/opportunities/cell-and-gene-therapy-in-hertfordshire/',
            '/international/investment/cell-and-gene-therapy-in-hertfordshire/',
        ),
        (
            '/international/content/investment/opportunities/circular-economy-in-telford/',
            '/international/investment/circular-economy-in-telford/',
        ),
        (
            '/international/content/investment/opportunities/compound-semiconductors-and-applications-in-south-wales/',
            '/international/investment/compound-semiconductors-and-applications-in-south-wales/',
        ),
        (
            '/international/content/investment/opportunities/connected-and-immersive-technologies-for-future-mobility-in-coventry-and-warwickshire/',  # noqa:E501
            '/international/investment/connected-and-immersive-technologies-for-future-mobility-in-coventry-and-warwickshire/',  # noqa:E501
        ),
        (
            '/international/content/investment/opportunities/cyber-security-in-gloucestershire/',
            '/international/investment/cyber-security-in-gloucestershire/',
        ),
        (
            '/international/content/investment/opportunities/data-analytics-and-artificial-intelligence-applications-in-leeds-city-region/',  # noqa:E501
            '/international/investment/data-analytics-and-artificial-intelligence-applications-in-leeds-city-region/',
        ),
        (
            '/international/content/investment/opportunities/food-processing-automation-in-greater-lincolnshire/',
            '/international/investment/food-processing-automation-in-greater-lincolnshire/',
        ),
        (
            '/international/content/investment/opportunities/fusion-energy-in-oxfordshire/',
            '/international/investment/fusion-energy-in-oxfordshire/',
        ),
        (
            '/international/content/investment/opportunities/future-of-aerospace-northern-ireland/',
            '/international/investment/future-of-aerospace-northern-ireland/',
        ),
        (
            '/international/content/investment/opportunities/hydrogen-applications-in-thames-estuary/',
            '/international/investment/hydrogen-applications-in-thames-estuary/',
        ),
        (
            '/international/content/investment/opportunities/mining-in-cornwall/',
            '/international/investment/mining-in-cornwall/',
        ),
        (
            '/international/content/investment/opportunities/net-zero-transport-in-coventry-and-warwickshire/',
            '/international/investment/net-zero-transport-in-coventry-and-warwickshire/',
        ),
        (
            '/international/content/investment/opportunities/nucleic-acid-therapies-in-oxfordshire/',
            '/international/investment/nucleic-acid-therapies-in-oxfordshire/',
        ),
        (
            '/international/content/investment/opportunities/offshore-wind-floating-substructures-in-scotland/',
            '/international/investment/offshore-wind-floating-substructures-in-scotland/',
        ),
        (
            '/international/content/investment/opportunities/plant-science-for-nutrition-in-norfolk-and-suffolk/',
            '/international/investment/plant-science-for-nutrition-in-norfolk-and-suffolk/',
        ),
        (
            '/international/content/investment/opportunities/precision-farming-in-telford/',
            '/international/investment/precision-farming-in-telford/',
        ),
        (
            '/international/content/investment/opportunities/rail-in-doncaster/',
            '/international/investment/rail-in-doncaster/',
        ),
        (
            '/international/content/investment/opportunities/regtech-in-northern-ireland/',
            '/international/investment/regtech-in-northern-ireland/',
        ),
        (
            '/international/content/investment/opportunities/smart-and-sustainable-aviation-in-south-west-england/',
            '/international/investment/smart-and-sustainable-aviation-in-south-west-england/',
        ),
        (
            '/international/content/investment/opportunities/vaccine-development-and-manufacture-in-liverpool-city-region/',  # noqa:E501
            '/international/investment/vaccine-development-and-manufacture-in-liverpool-city-region/',
        ),
        (
            '/international/content/investment/opportunities/anglesey-freeport/',
            '/international/investment/anglesey-freeport/',
        ),
        (
            '/international/content/investment/opportunities/celtic-freeport/',
            '/international/investment/celtic-freeport/',
        ),
        (
            '/international/content/investment/opportunities/east-midlands-freeport/',
            '/international/investment/east-midlands-freeport/',
        ),
        (
            '/international/content/investment/opportunities/forth-green-freeport/',
            '/international/investment/forth-green-freeport/',
        ),
        (
            '/international/content/investment/opportunities/felixstowe-and-harwich-freeport/',
            '/international/investment/felixstowe-and-harwich-freeport/',
        ),
        (
            '/international/content/investment/opportunities/humber-freeport/',
            '/international/investment/humber-freeport/',
        ),
        (
            '/international/content/investment/opportunities/inverness-and-cromarty-firth-green-freeport/',
            '/international/investment/inverness-and-cromarty-firth-green-freeport/',
        ),
        (
            '/international/content/investment/opportunities/liverpool-city-region-freeport/',
            '/international/investment/liverpool-city-region-freeport/',
        ),
        (
            '/international/content/investment/opportunities/plymouth-and-south-devon-freeport/',
            '/international/investment/plymouth-and-south-devon-freeport/',
        ),
        ('/international/content/investment/opportunities/solent/', '/international/investment/solent/'),
        (
            '/international/content/investment/opportunities/teesside-freeport/',
            '/international/investment/teesside-freeport/',
        ),
        (
            '/international/content/investment/opportunities/thames-freeport/',
            '/international/investment/thames-freeport/',
        ),
        (
            '/international/contact/',
            '/international/site-help/',
        ),
        (
            '/international/content/investment/how-we-can-help/global-entrepreneur-program/',
            '/campaign-site/gep/',
        ),
        (
            '/international/content/investment/how-we-can-help/the-venture-capital-unit/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/content/investment/how-we-can-help/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/content/investment/why-invest-in-the-uk/',
            '/international/',
        ),
        (
            '/international/content/investment/how-we-can-help/research-and-development-rd-support-in-the-uk/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/trade/contact/',
            '/international/',
        ),
        (
            '/international/invest/contact/',
            '/international/',
        ),
        (
            '/international/content/investment/how-we-can-help/the-office-for-investment/',
            '/international/',
        ),
        (
            '/international/content/investment/how-we-can-help/hire-skilled-workers-for-your-uk-operations/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/content/investment/how-we-can-help/access-finance-in-the-uk/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/content/investment/how-we-can-help/establish-a-base-for-business-in-the-uk/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/content/investment/how-we-can-help/register-a-company-in-the-uk/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/content/investment/how-we-can-help/uk-visas-and-migration/',
            '/international/expand-your-business-in-the-uk/',
        ),
        (
            '/international/content/investment/how-we-can-help/open-a-uk-business-bank-account/',
            '/international/expand-your-business-in-the-uk/',
        ),
        ('/international/content/invest/how-to-setup-in-the-uk/', '/international/expand-your-business-in-the-uk/'),
        (
            '/international/content/invest/how-to-setup-in-the-uk/random-sub-route/',
            '/international/expand-your-business-in-the-uk/',
        ),
    ),
)
@pytest.mark.django_db
def test_international_redirects(previous_url, migrated_url, client):
    """
    test redirects implemented as part of the migration from great-international-ui to great-cms
    """
    response = client.get(previous_url)
    assert response.status_code == 301
    assert response.url == migrated_url
