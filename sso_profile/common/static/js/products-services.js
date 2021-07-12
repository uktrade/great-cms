dit = window.dit || {};
dit.components = dit.components || {};

dit.components.productsServicesTypeahead = (function() {
  function ProductsServicesTypeahead(options) {

    var multiselectElement = options.multiselectElement;
    var choices = options.choices;
    var selectedValuesElement = options.selectedValuesElement;
    var noResultsLabel = options.noResultsLabel;
    var autocompleteId = multiselectElement.id + '_autocomplete';
    var showAllValues = options.showAllValues || false;//true;
    var containerElement = document.createElement('span');
    var placeholder = options.placeholder || '';
    multiselectElement.parentNode.insertBefore(containerElement, multiselectElement);

    accessibleAutocomplete({
      element: containerElement,
      selectElement: multiselectElement,
      defaultValue: '',
      confirmOnBlur: false,
      showAllValues: showAllValues,
      id: autocompleteId,
      onConfirm: handleAdd,
      placeholder: placeholder,
      source: function(query, populateResults) {
        var selectedValues = getSelectedValues();
        var filtered = [].filter.call(
          choices,
          function(choice) { return selectedValues.indexOf(choice) == -1; }
        );
        var results = filtered.filter(function(result) {
          return result.toLowerCase().indexOf(query.toLowerCase()) !== -1
        });
        if (query && results.length == 0) {
          results.push(query)
        }
        populateResults(results);
      }
    });
    multiselectElement.style.display = 'none'
    var autocompleteInputElement = document.getElementById(autocompleteId);
    renderSelectedValues();

    function getSelectedValues() {
      return multiselectElement.value ? multiselectElement.value.split('|') : [];
    }

    function setOption(label, selected) {
      var selectedValues = getSelectedValues()
      var alreadySelected = selectedValues.indexOf(label) > -1;
      if (selected && !alreadySelected) {
        selectedValues.push(label);
      } else if(alreadySelected) {
        selectedValues = selectedValues.filter(function(item) {
          return item !== label;
        })
      }
      multiselectElement.value = selectedValues.join('|');
      renderSelectedValues();
    }

    function handleAdd(value) {
      setOption(value, true);
      // hack to clear the input box. delay 150ms to allow the react component
      // to render iwth the new value first.
      // hide the selected value by making it the same colour as the input box
      autocompleteInputElement.style.color = 'white';
      setTimeout(function() {
        autocompleteInputElement.value = '';
        autocompleteInputElement.style.color = 'black';
      }, 150);
    }

    function handleRemove(event) {
      setOption(event.target.value, false);
    }

    function createSelectedValueElement(label) {
      var element = document.createElement('button');
      element.setAttribute('tabindex', 0);
      element.setAttribute('title', 'Click to remove this expertise');
      element.value = label;
      element.innerHTML = label;
      element.addEventListener('click', handleRemove);
      return element;
    }

    function buildNothingSelectedElement() {
      var element = document.createElement('span');
      element.innerHTML = noResultsLabel;
      return element;
    }

    function renderSelectedValues() {
      selectedValuesElement.innerHTML = '';
      var fragment = document.createDocumentFragment();
      var selectedValues = getSelectedValues();

      for (var i = 0; i < selectedValues.length; i++) {
        var label = selectedValues[i];
        var element = createSelectedValueElement(label);
        fragment.appendChild(element);
      }
      if (fragment.childNodes.length === 0) {
        var element = buildNothingSelectedElement();
        fragment.appendChild(element);
      }
      selectedValuesElement.appendChild(fragment);
    }

  }
  return function(options) {
    return new ProductsServicesTypeahead(options);
  }
})();
