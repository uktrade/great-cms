from django import template

register = template.Library()


@register.simple_tag()
def exportplan_name(export_plan):
    name = export_plan.get('name')
    products = export_plan.get('export_commodity_codes')
    commodity_name = products[0].get('commodity_name') if products else ''
    countries = export_plan.get('export_countries')
    country_name = countries[0].get('country_name') if countries else ''
    return name or f'Export plan for selling { commodity_name } to { country_name }'
