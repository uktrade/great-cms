from django.conf import settings
from opensearch_dsl import Document, Q, Search, field
from opensearch_dsl.connections import connections


class CaseStudyIndexed(Document):
    pk = field.Keyword(index=False)
    hscodes = field.Keyword()
    country = field.Keyword()
    region = field.Keyword()
    lesson = field.Keyword()
    tradingblocs = field.Keyword()

    class Index:
        name = settings.OPENSEARCH_CASE_STUDY_INDEX
        settings = {
            'number_of_shards': 1,
        }


def stringify_lessons(lessons):
    page_type_mapping = {'detailpage': 'lesson', 'curatedlistpage': 'module', 'topicpage': 'topic'}
    out = []
    for lesson in lessons:
        out.append(f'{page_type_mapping.get(lesson.specific._meta.model_name)}_{str(lesson.id)}')
    return ' '.join(out)


def stringify_tags(tags):
    return ' '.join([str(item).replace(' ', '_') for item in tags])


def get_connection():
    return connections.get_connection()


def case_study_to_index(case_study):
    cs_indexed = CaseStudyIndexed(
        pk=str(case_study.id),
        hscodes=stringify_tags(case_study.hs_code_tags.all()),
        lesson=stringify_lessons([related_page.page.specific for related_page in case_study.related_pages.all()]),
        country=stringify_tags(case_study.country_code_tags.all()),
        region=stringify_tags(case_study.region_code_tags.all()),
        tradingblocs=stringify_tags(case_study.trading_bloc_code_tags.all()),
        modified=case_study.modified,
    )
    return cs_indexed


def update_cs_index(cs):
    # if we don't have an ID then we are creating
    if cs.id:
        delete_cs_index(cs.id)
        case_study_to_index(cs).save()


def delete_cs_index(cs_id):
    Search(
        using=get_connection(),
        index=settings.OPENSEARCH_CASE_STUDY_INDEX,
    ).query(Q('match', pk=cs_id)).delete()


def search(export_commodity_codes, export_markets, export_regions, page_context):
    hs_parts = set()
    for hs_code in export_commodity_codes:
        for i in [slice(6), slice(4)]:  # Not interested in docs that only have an HS2 match
            hs_parts.add(hs_code[i])
    query = Q('match', lesson=stringify_tags(page_context))
    if export_markets:
        query = query | Q('match', country=stringify_tags(export_markets))
    if hs_parts:
        query = query | Q('match', hscodes=' '.join(hs_parts))
    return Search(
        using=get_connection(),
        index=settings.OPENSEARCH_CASE_STUDY_INDEX,
    ).query(query)
