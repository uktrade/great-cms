from django.shortcuts import get_object_or_404, render

from cms_extras.modeladmin import CaseStudyAdmin
from core.models import CaseStudy


def case_study(request, case_study_id, template='view_case_study.html'):
    """Allows a CaseStudy to be rendered standalone, within the CMS admin"""

    case_study = get_object_or_404(CaseStudy, id=case_study_id)
    backlink = CaseStudyAdmin().url_helper.get_action_url('index')

    return render(request=request, context={'backlink': backlink, 'case_study': case_study}, template_name=template)
