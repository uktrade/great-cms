from django.http import HttpResponseRedirect, JsonResponse
from django.views import View

from learn.forms import CsatUserFeedbackForm
from learn.models import CsatUserFeedback


class HCSATView(View):

    def get_csat(self):
        csat_id = self.request.session.get('learn_to_export_csat_id')
        if csat_id:
            return CsatUserFeedback.objects.get(id=csat_id)
        return None

    def get_success_url(self):
        return self.url

    @property
    def js_enabled(self):
        if 'js_enabled' in self.request.get_full_path():
            return True
        return False

    def update_csat(self, form, csat):

        csat_feedback, created = CsatUserFeedback.objects.update_or_create(
            id=csat.id,
            defaults={
                'experienced_issues': form.cleaned_data['experience'],
                'other_detail': form.cleaned_data['experience_other'],
                'likelihood_of_return': form.cleaned_data['likelihood_of_return'],
                'service_improvements_feedback': form.cleaned_data['feedback_text'],
            },
        )
        csat_stage = self.request.session.get('learn_to_export_csat_stage', 0)

        if csat_stage == 0:
            self.request.session['learn_to_export_csat_stage'] = 1
        else:
            self.request.session['learn_to_export_csat_stage'] = 2

        return csat_feedback

    def create_csat(self, form):

        csat_feedback = CsatUserFeedback.objects.create(
            satisfaction_rating=form.cleaned_data['satisfaction'],
            experienced_issues=form.cleaned_data['experience'],
            other_detail=form.cleaned_data['experience_other'],
            likelihood_of_return=form.cleaned_data['likelihood_of_return'],
            service_improvements_feedback=form.cleaned_data['feedback_text'],
            URL=self.success_url,
            user_journey='ARTICLE_PAGE',
        )
        self.request.session['learn_to_export_csat_id'] = csat_feedback.id
        self.request.session['learn_to_export_csat_stage'] = 1

        return csat_feedback

    def post(self):
        data = self.request.POST
        form = CsatUserFeedbackForm(data=data)

        if 'cancelButton' in data:
            self.request.session['learn_to_export_csat_stage'] = 2
            return HttpResponseRedirect(self.get_success_url())

        if form.is_valid():

            csat = self.get_csat()
            if csat:
                csat_feedback = self.update_csat(form, csat)
            else:
                csat_feedback = self.create_csat(form)

            data = {
                'pk': csat_feedback.pk,
            }
            if self.js_enabled:
                csat_stage = self.request.session.get('learn_to_export_csat_stage', 0)
                if csat_stage == 1:
                    del self.request.session['learn_to_exportb_csat_stage']
                return JsonResponse(data)
            return HttpResponseRedirect(self.get_success_url())

        if self.js_enabled:
            return JsonResponse(form.errors, status=400)
