function customSuggest (query, syncResults) {
    const sectors = [
      { 'Aerospace': ['Planes', 'Jets', 'Space'] },
      { 'Engineering': ['Planes', 'Boats', 'Cars', 'Software'] },
      { 'Food & Drink': ['Alcohol', 'Rice', 'Coffee', 'Tea', 'Bread'] },
    ];
    syncResults(query
      ? sectors.filter(function (result) {
          let resultContains = Object.keys(result)[0].toLowerCase().indexOf(query.toLowerCase()) !== -1;
          let tags = Object.values(result)[0];
          let endonymContains = false;
          for (let i = 0; i < tags.length; i++) {
            if (endonymContains == true) { break; }
            endonymContains = tags[i].toLowerCase().indexOf(query.toLowerCase()) !== -1
          }
          return resultContains || endonymContains;
        })
      : []
    )
  }

function inputValueTemplate (result) {
    return result && Object.keys(result)[0]
}

function suggestionTemplate (result) {
    return result && Object.keys(result)[0];
}

accessibleAutocomplete.enhanceSelectElement({
    selectElement: document.getElementById('sector'),
    source: customSuggest,
    defaultValue: '',
    minLength: 2,
    onConfirm: () => {},
    templates: {
    inputValue: inputValueTemplate,
    suggestion: suggestionTemplate
    }
});
