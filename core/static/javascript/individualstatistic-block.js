class IndividualStatisticBlockDefinition extends window.wagtailStreamField.blocks
    .StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {

        let CSRF_TOKEN = '{{ csrf_token }}';

        const block = super.render(
            placeholder,
            prefix,
            initialState,
            initialError,
        );

        let numberField = document.getElementById(prefix + '-number');
        const holdNumber = numberField.value;
        const headingField = document.getElementById(prefix + '-heading');

        const createParagraph = (cls, id) => {
            let p = document.createElement("p");
            p.setAttribute("class", cls);
            p.innerText = "Data is provided by IMF API and cannot be edited";
            p.id = id;
            return p;
        };

        const updateNumberInput = () => {
            if (headingField.value == 'Economic growth' || headingField.value == 'GDP per capita' ) {
                let id = "";
                if (headingField.value == 'Economic growth') {
                    id = "statistic-heading-warning-growth-id";
                }
                else {
                    id = "statistic-heading-warning-gdp-id";
                };
                const warningField = document.getElementById(id);
                if (!warningField) {
                    const p = createParagraph("help-block help-critical", id);
                    headingField.before(p);
                }
                numberField.value = holdNumber;

            };
        };

        numberField.addEventListener('change', updateNumberInput);
        if (headingField.value == 'Economic growth' || headingField.value == 'GDP per capita' ) {
            const p = createParagraph("help-block govuk-body", "statistic-heading-label-id");
            headingField.after(p);
        };
        return block;
    }
}
window.telepath.register('core.blocks.IndividualStatisticBlock', IndividualStatisticBlockDefinition);
