GreatFrontend = window.GreatFrontend || {}

GreatFrontend.MakeOrDoSearchEnhanced = {
    init: (sic_sector_data={}, default_value='') => {
        document.querySelector('#sic_description').remove();

        const sic_descriptions = sic_sector_data.data.map(el => {
            const keywords = el.keywords ? '|' + el.keywords : '';
            return el.sic_description + keywords;
        });
        accessibleAutocomplete({
            element: document.querySelector('#sic_description-container'),
            id: 'sic_description',
            name: 'sic_description',
            source: sic_descriptions,
            autoselect: false,
            minLength: 3,
            displayMenu: 'overlay',
            defaultValue: default_value,
            templates: {
                suggestion: (selectedSIC) => {
                    const search_input = document.querySelector('#sic_description');
    
                    const match = sic_sector_data.data.find(el => {
                        return selectedSIC.includes(el.sic_description);
                    });
    
                    if (match && match.sic_description && match.dit_sector_list_field_04) {
                        let keywords = '';
                        let keyword_parts = [];
                        
                        if (match.keywords) {
                            keywords = match.keywords;
                            keyword_parts = keywords.split(', ');
                        }
    
                        if (search_input && keyword_parts) {
                            let keyword_match = '';
    
                            keyword_parts.forEach(keyword => {
                                if (keyword.includes(search_input.value)) {
                                    keyword_match = keyword;
                                }
                            });
    
                            if (keyword_match) {
                                return `<span>${match.sic_description} (${keyword_match})</span><br /><span class="govuk-body-s">${match.dit_sector_list_field_04}</span>`;
                            }
                        }
    
                        return `<span>${match.sic_description}</span><br /><span class="govuk-body-s">${match.dit_sector_list_field_04}</span>`;
                    }
    
                    return '<span>No results found</span>';
                },
                inputValue: (selectedSIC='') => {
                    if (selectedSIC) {
                        return selectedSIC.split('|')[0];
                    }
                }
            },
            onConfirm: (selectedSIC) => {
                if (selectedSIC) {
                    const {dit_sector_list_field_04, exporter_type='goods', keywords=null} = sic_sector_data.data.find(el => selectedSIC.includes(el.sic_description));
                    let is_keyword_match = false;
    
                    
                    document.querySelector('#sector').value = dit_sector_list_field_04;
                    document.querySelector('#make_or_do_keyword').value = document.querySelector('#sic_description').value.split('|')[0];
                    document.querySelector('#exporter_type').value = exporter_type;
    
                    if (keywords) {
                        is_keyword_match = keywords.includes(document.querySelector('#make_or_do_keyword').value);
    
                        let keyword_match = '';
    
                        keyword_parts = keywords.split(', ');
    
                        keyword_parts.forEach(keyword => {
                            if (keyword.includes(document.querySelector('#make_or_do_keyword').value)) {
                                keyword_match = keyword;
                            }
                        });
    
                        document.querySelector('#make_or_do_keyword').value = keyword_match;
    
                    }
    
                    document.querySelector('#is_keyword_match').value = is_keyword_match ? 'True' : 'False';
    
                    setTimeout(() => {
                        if (is_keyword_match) {
                            document.querySelector('#sic_description').value = document.querySelector('#sic_description').value + " (" + document.querySelector('#make_or_do_keyword').value + ")";
                        }
                    }, 10);
                }
            },
            placeholder: 'For example, financial services or coffee',
            inputClasses: 'govuk-input great-text-input great-ds-autocomplete-input',
            menuClasses: 'great-autocomplete-overlay',
            required: true,
            showNoOptionsFound: false,
        });

        const clear_search_button = document.querySelector('[data-make-or-do-form] button');

        if (clear_search_button) {
            document.querySelector('#clear_search').addEventListener('click', (e) => {
                e.preventDefault();
        
                document.querySelector('#sector').value = '';
                document.querySelector('#make_or_do_keyword').value = '';
                document.querySelector('#exporter_type').value = '';
                document.querySelector('#sic_description').value = '';
        
                document.querySelector('#clear_search').style.display = 'none';
            });
        }

        document.querySelector('#clear_search').style.display = 'none';
    
        document.querySelector('#sic_description').addEventListener('focus', (e) => {
            document.querySelector('#clear_search').style.display = 'block';
        });
    
        document.querySelector('#sic_description').addEventListener('blur', (e) => {
            setTimeout(() => {
                document.querySelector('#clear_search').style.display = 'none';
            }, 200);
        });
    }
}
