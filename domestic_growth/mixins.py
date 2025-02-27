import pickle


class TriageMixin:
    initial_data = {}

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get('domestic_growth_triage_data')

        if data:
            self.initial_data = initial = pickle.loads(bytes.fromhex(data))[0]
        return initial

    def save_data(self, form):
        cleaned_data = form.cleaned_data

        form_data = ({**self.initial_data, **cleaned_data},)
        form_data = pickle.dumps(form_data).hex()
        self.request.session['domestic_growth_triage_data'] = form_data

    def get_context_data(self, **kwargs):
        form_data = {}

        if self.request.session.get('domestic_growth_triage_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('domestic_growth_triage_data')))[0]

        return super().get_context_data(
            **kwargs,
            session_data=form_data,
        )
