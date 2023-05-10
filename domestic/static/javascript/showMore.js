function findEventTitle(element) {
  let current = element;

  // While the current element is not null, keep searching its ancestors
  // for an element with the class `event-title`.
  while (current) {
    if (current.querySelector('.event-title')) {
      return current.querySelector('.event-title').innerText;
    }

    // Move up the level.
    current = current.parentElement;
  }
  return null;
}

const handleToggle = (element) => {
  const text = element.previousElementSibling
  const summary = element.querySelector('summary')
  const summaryText = summary.innerText

  if (summaryText === 'Show more') {
    summary.innerText = 'Show less'
  } else {
    summary.innerText = 'Show more'
  }

  const eventTitle = findEventTitle(element);

  (window.dataLayer = window.dataLayer || []).push({
    event: 'lessontitle',
    eventTitle: eventTitle,
    action: summaryText
});

  return text.classList.toggle('details-text-open')
}

const detailsElements = document.querySelectorAll('[data-show-more]')
detailsElements.forEach((element) =>
  element.addEventListener('toggle', () => handleToggle(element))
)

const trackedElements = document.querySelectorAll('.ukea-ga-tracking')
trackedElements.forEach((element) =>
    element.addEventListener('click', trackButtonClick, false)
);

function trackButtonClick(element) {
  const eventInfo = element.target.innerText.split('\n',1);
  const eventTitle = findEventTitle(element.target);
  (window.dataLayer = window.dataLayer || []).push({
    event: 'lessontitle',
    eventTitle: eventTitle,
    action: eventInfo[0]
  });
}
