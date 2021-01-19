var GOVUK = GOVUK || {}
GOVUK.utils = GOVUK.utils || {};

GOVUK.utils.toggleFieldsetClassOnClick = (function() {
  return function toggleFieldsetClassOnClick(elements, otherRadio, legendDescription, legendClass) {

    function moveToFieldset(elements, fieldset) {
      var legend = document.createElement('legend');
      var sibling = elements[0];

      if (legendDescription != null) {
        var legendDescriptionNode = document.createTextNode(legendDescription);
        legend.appendChild(legendDescriptionNode);

        if (legendClass != null) {
          legend.classList.add(legendClass);
        }
      }

      fieldset.appendChild(legend);
      sibling.parentElement.insertBefore(fieldset, sibling);
      for (var i=0; i<elements.length; i++) {
        fieldset.appendChild(elements[i]);
      }
    }

    function findFieldsetAncestor(el) {
        while ((el = el.parentElement) && el.tagName != 'FIELDSET');
        return el;
    }

    function addFieldsetClassName(className) {
      fieldset.className = (fieldset.className || '') + ' ' + className;
    }

    function removeFieldsetClassName(className) {
      var re = new RegExp(className, 'g');
      fieldset.className = fieldset.className.replace(re, '');
    }

    function handleChange(event) {
      if (otherRadio.checked) {
        addFieldsetClassName('checked');
        removeFieldsetClassName('unchecked');
      } else {
        removeFieldsetClassName('checked');
        addFieldsetClassName('unchecked');
      }
    }

    var fieldset = document.createElement('fieldset');
    moveToFieldset(elements, fieldset);

    if (otherRadio != null) {
        if (otherRadio.checked) {
            addFieldsetClassName('checked');
        }

        var radios = document.getElementsByName(otherRadio.name);
        for (var i = 0; i < radios.length; i++) {
            radios[i].addEventListener('change', handleChange);
        }
    }
  };
})();


GOVUK.utils.toggleOtherOnSelect = (function() {
  return function toggleOtherOnClick(inputBox, options) {
    function hide(element) {
      element.style.display = 'none';
    }

    function show(element) {
      element.style.display = 'block';
    }

    function hideInputBox() {
      hide(inputBox.parentElement);
    }

    function showInputBox() {
      show(inputBox.parentElement);
      inputBox.focus();
    }

    function handleSelectboxChange(event) {
      if (event.target.value.toUpperCase() === 'OTHER') {
        showInputBox();
      } else {
        hideInputBox();
        inputBox.value = '';
      }
    }

    if (inputBox.value === '') {
      hideInputBox();
    }

    options.addEventListener('change', handleSelectboxChange);
  };
})();


GOVUK.utils.toggleRadioOtherOnClick = (function() {
  return function toggleRadioOtherOnClick(otherRadio, otherOptions) {

    function hide(element) {
      element.style.display = 'none';
    }

    function show(element) {
      element.style.display = 'block';
    }

    function hideOtherOptions() {
      hide(otherOptions);
    }

    function showOtherOptions() {
      show(otherOptions);
    }

    function handleCheckboxChange(event) {
      if (otherRadio.checked) {
        showOtherOptions();
      } else {
        hideOtherOptions();
      }
    }

    handleCheckboxChange()
    var radios = document.getElementsByName(otherRadio.name);
    for(var i=0; i<radios.length; i++) {
      radios[i].addEventListener('change', handleCheckboxChange);
    }
  };
})();

GOVUK.utils.toggleInputOnNotTicked = (function() {
  return function toggleRadioOtherOnClick(radio, targetElement) {

    function hide(element) {
      element.style.display = 'none';
    }

    function show(element) {
      element.style.display = 'block';
    }

    function hideOtherOptions() {
      hide(targetElement);
    }

    function showOtherOptions() {
      show(targetElement);
    }

    function handleCheckboxChange(event) {
      if (radio.checked) {
        hideOtherOptions();
      } else {
        showOtherOptions();
      }
    }

    handleCheckboxChange()
    radio.addEventListener('change', handleCheckboxChange);
  };
})();
