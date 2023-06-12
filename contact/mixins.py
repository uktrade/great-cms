import pickle


class ExportSupportFormMixin:
    initial_data = {}

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get('form_data')
        if data:
            self.initial_data = initial = pickle.loads(bytes.fromhex(data))[0]
        return initial

    def save_data(self, form):
        cleaned_data = form.cleaned_data

        form_data = ({**self.initial_data, **cleaned_data},)
        form_data = pickle.dumps(form_data).hex()

        self.request.session['form_data'] = form_data
