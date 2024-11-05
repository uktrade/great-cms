GreatFrontend = window.GreatFrontend || {}

GreatFrontend.MakeOrDoSearch = {
    init: (sic_sector_data={}) => {
        document.querySelector('#sic_description').remove();

        const sic_descriptions = sic_sector_data.data.map(el => el.sic_description);
        
        accessibleAutocomplete({
            element: document.querySelector('#sic_description-container'),
            id: 'sic_description',
            name: 'sic_description',
            source: sic_descriptions,
            autoselect: false,
            minLength: 3,
            displayMenu: 'overlay',
            defaultValue: '',
            templates: {
                suggestion: (selectedSIC) => {
                    const {sic_description, dit_sector_list_field_04} = sic_sector_data.data.find(el => el.sic_description === selectedSIC)
                    return `<span>${sic_description}</span><br /><span>${dit_sector_list_field_04}</span>`;
                }
            },
            onConfirm: (selectedSIC) => {
                if (selectedSIC) {
                    const {dit_sector_list_field_04, exporter_type='goods'} = sic_sector_data.data.find(el => el.sic_description === selectedSIC);

                    document.querySelector('#sector').value = dit_sector_list_field_04;
                    document.querySelector('#make_or_do_keyword').value = document.querySelector('#sic_description').value;
                    document.querySelector('#exporter_type').value = exporter_type;
                }
            },
            placeholder: 'For example, financial services or coffee',
            inputClasses: 'govuk-input great-text-input great-ds-autocomplete-input',
            menuClasses: 'great-autocomplete-overlay',
            required: true,
        });

        document.querySelector('[data-make-or-do-form] button').addEventListener('click', (e) => {
            e.preventDefault();

            const form = document.querySelector('[data-make-or-do-form]');

            const sector_value = form.querySelector('#sector').value;
            const make_or_do_keyword_value = form.querySelector('#make_or_do_keyword').value;
            const exporter_type_value = form.querySelector('#exporter_type').value;
            const sic_description_value = form.querySelector('#sic_description').value;

            const qs = `?sector=${sector_value}&make_or_do=${make_or_do_keyword_value}&exporter_type=${exporter_type_value}&sic_description=${sic_description_value}`;
            
            window.location = `/your-export-guide/what-does-your-company-make-or-do/get${qs}`;
        });
    }
}
