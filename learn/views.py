from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import FormView
from learn.forms import CsatUserFeedbackForm
from learn.models import CsatUserFeedback


class ArticlePageView(FormView):
    form_class = CsatUserFeedbackForm
    template_name = 'learn/detail_page.html'

    def get_csat(self):
        csat_id = self.request.session.get('learn_to_export_csat_id')
        if csat_id:
            return CsatUserFeedback.objects.get(id=csat_id)
        return None

    def get_initial(self):
        csat = self.get_csat()
        if csat:
            satisfaction = csat.satisfaction_rating
            if satisfaction and self.request.session.get('learn_to_export_csat_stage', 0) == 1:
                return {'satisfaction': satisfaction}
        return {'satisfaction': ''}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stage = self.request.session.get('learn_to_export_csat_stage', 0)
        context['csat_form'] = CsatUserFeedbackForm
        context['csat_stage'] = stage
        if stage == 2:
            del self.request.session['learn_to_export_csat_stage']

        return context

    def form_invalid(self, form):
        if 'cancelButton' in self.request.POST:
            self.request.session['learn_to_export_csat_stage'] = 2
            return HttpResponseRedirect(self.get_success_url())
        super().form_invalid(form)
        js_enabled = 'js_enabled' in self.request.get_full_path()
        if js_enabled:
            return JsonResponse(form.errors, status=400)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if 'cancelButton' in self.request.POST:
            self.request.session['learn_to_export_csat_stage'] = 2
            return HttpResponseRedirect(self.get_success_url())

        super().form_valid(form)
        csat = self.get_csat()
        if csat:
            csat = self.get_csat()
            if csat:
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

            else:
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

            data = {
                'pk': csat_feedback.pk,
            }
            js_enabled = 'js_enabled' in self.request.get_full_path()
            if js_enabled:
                csat_stage = self.request.session.get('learn_to_export_csat_stage', 0)
                if csat_stage == 1:
                    del self.request.session['learn_to_exportb_csat_stage']
                return JsonResponse(data)
            return HttpResponseRedirect(self.get_success_url())
        return super().form_valid(form)

    def get_success_url(self):
        return self.url
