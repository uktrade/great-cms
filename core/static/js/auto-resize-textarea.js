// modified from:
// https://www.impressivewebs.com/textarea-auto-resize/

// Targets all textareas
let textareas = document.querySelectorAll('textarea'),
  hiddenDiv = document.createElement('div'),
  content = null;

// Add the styles for the hidden div
hiddenDiv.style.display = 'none';
hiddenDiv.style.whiteSpace = 'pre-wrap';
hiddenDiv.style.wordWrap = 'break-word';

function calculateHeight(element) {
  // Append hiddendiv to parent of textarea, so the size is correct
  element.parentNode.appendChild(hiddenDiv);

  // Remove this if you want the user to be able to resize it in modern browsers
  element.style.resize = 'none';

  // This removes scrollbars
  element.style.overflow = 'hidden';

  // If the input is empty, calculate height according to the placeholder text
  if (!element.value) {
    hiddenDiv.innerHTML = element.placeholder;
  } else {
    // Add the same content to the hidden div
    hiddenDiv.innerHTML = element.value;
  }

  // Briefly make the hidden div block but invisible
  // This is in order to read the height
  hiddenDiv.style.visibility = 'hidden';
  hiddenDiv.style.display = 'block';
  element.style.height = hiddenDiv.offsetHeight + 30 + 'px';

  // Make the hidden div display:none again
  hiddenDiv.style.visibility = 'visible';
  hiddenDiv.style.display = 'none';
}

// Loop through all the textareas and add the event listener
for(let element of textareas) {
  (function(element) {
    // set initial height on load
    calculateHeight(element);

    element.addEventListener('input', function() {
      calculateHeight(element);
    });
  })(element);
}
