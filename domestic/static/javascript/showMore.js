const handleToggle = (element) => {
  const text = element.previousElementSibling
  const summary = element.querySelector('summary')
  const summaryText = summary.innerText

  if (summaryText === 'Show more') {
    summary.innerText = 'Show less'
  } else {
    summary.innerText = 'Show more'
  }

  return text.classList.toggle('details-text-open')
}

const detailsElements = document.querySelectorAll('[data-show-more]')
detailsElements.forEach((element) =>
  element.addEventListener('toggle', () => handleToggle(element))
)
