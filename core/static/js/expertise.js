dit = window.dit || {};
dit.components = dit.components || {};

dit.components.expertise = (function() {
  function ExpertiseTypeahead(options) {

    var multiselectElement = options.multiselectElement;
    var selectedValuesElement = options.selectedValuesElement;
    var noResultsLabel = options.noResultsLabel;
    var autocompleteId = multiselectElement.id + '_autocomplete';
    var containerElement = document.createElement('span');
    var placeholder = multiselectElement.getAttribute('placeholder');
    multiselectElement.parentNode.insertBefore(containerElement, multiselectElement);

    accessibleAutocomplete({
      element: containerElement,
      selectElement: multiselectElement,
      defaultValue: '',
      confirmOnBlur: false,
      showAllValues: true,
      id: autocompleteId,
      onConfirm: handleAdd,
      placeholder: placeholder || '',
      source: function(query, populateResults) {
        var filtered = [].filter.call(
          multiselectElement.options,
          function(option) { return (option.selected === false)
        });
        var results = filtered
          .map(function(option) { return option.textContent || option.innerText })
          .filter(function(result) { return result.toLowerCase().indexOf(query.toLowerCase()) !== -1 });
        populateResults(results);
      }
    });
    multiselectElement.style.display = 'none'
    var autocompleteInputElement = document.getElementById(autocompleteId);
    renderSelectedValues();

    function setOption(label, selected) {
      for (var i = 0; i < multiselectElement.options.length; i++) {
        if (multiselectElement.options[i].innerHTML == label) {
          multiselectElement.options[i].selected = selected;
        }
      }
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
      for (var i = 0; i < multiselectElement.options.length; i++) {
        var option = multiselectElement.options[i];
        if (option.selected) {
          var element = createSelectedValueElement(option.innerHTML);
          fragment.appendChild(element);
        }
      }
      if (fragment.childNodes.length === 0) {
        var element = buildNothingSelectedElement();
        fragment.appendChild(element);
      }
      selectedValuesElement.appendChild(fragment);
    }

  }
  return function(options) {
    return new ExpertiseTypeahead(options);
  }
})();
