dit = window.dit || {};
dit.components = dit.components || {};

dit.components.multiselectAutocomplete = (function() {
  function MultiSelectAutocomplete(options) {

    var selectInputElement = options.selectInputElement;
    var autocompleteId = selectInputElement.id + '_autocomplete';

    var selectedValuesElement = document.createElement('div');
    selectedValuesElement.setAttribute('class', 'g-multi-select-autocomplete-selected-values');
    var container = document.createElement('div');
    container.appendChild(selectedValuesElement);
    var accessibleAutocompleteElement = document.createElement('span');
    container.appendChild(accessibleAutocompleteElement);
    // adding the container to the input box's parent
    selectInputElement.parentNode.insertBefore(container, selectInputElement);

    accessibleAutocomplete({
      element: accessibleAutocompleteElement,
      selectElement: selectInputElement,
      defaultValue: '',
      confirmOnBlur: false,
      id: autocompleteId,
      onConfirm: handleAdd,
      placeholder: 'Start typing',
      displayMenu: 'overlay',
      source: function(query, populateResults) {
        var filtered = [].filter.call(
          selectInputElement.options, 
          function(option) { return (option.selected === false)
        });
        var results = filtered
          .map(function(option) { return option.textContent || option.innerText })
          .filter(function(result) { return result.toLowerCase().indexOf(query.toLowerCase()) !== -1 }); 
        populateResults(results);
      }
    });
    selectInputElement.style.display = 'none'
    var autocompleteInputElement = document.getElementById(autocompleteId);
    renderSelectedValues(false);

    function setOption(label, selected) {
      for (var i = 0; i < selectInputElement.options.length; i++) {
        if (selectInputElement.options[i].innerHTML == label) {
          selectInputElement.options[i].selected = selected;
        }
      }
      renderSelectedValues(true);
    }

    function handleAdd(value) {
      setOption(value, true);
      // hack to clear the input box. delay 150ms to allow the react component
      // to render with the new value first.
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
      var removeElement = document.createElement('button');
      removeElement.setAttribute('title', 'Click to remove');
      removeElement.innerHTML = ' ❌';
      removeElement.addEventListener('click', handleRemove);
      removeElement.value = label;
      var element = document.createElement('span');
      element.setAttribute('class', 'g-multi-select-autocomplete-selected-item')
      element.setAttribute('tabindex', 0);
      element.innerHTML = label
      element.appendChild(removeElement);
      return element;
    }

    function renderSelectedValues(autoFocusInput) {
      selectedValuesElement.innerHTML = '';
      var fragment = document.createDocumentFragment();
      for (var i = 0; i < selectInputElement.options.length; i++) {
        var option = selectInputElement.options[i];
        if (option.selected) {
          var element = createSelectedValueElement(option.innerHTML);
          fragment.appendChild(element);
        }
      }
      fragment.appendChild(accessibleAutocompleteElement)
      selectedValuesElement.appendChild(fragment);
      if (autoFocusInput && fragment.childNodes.length === 0) {
        autocompleteInputElement.focus();
      }
    }

  }
  return function(options) {
    return new MultiSelectAutocomplete(options);
  }


})();

(function() {
  var elements = document.querySelectorAll('.g-multi-select-autocomplete select');
  for (var i = 0; i < elements.length; i++) {
    dit.components.multiselectAutocomplete({selectInputElement: elements[i]});
  }
})()
