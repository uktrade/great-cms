const handleToggle = (element) => {
  const text = element.previousElementSibling
  return (
    text.classList.toggle("details-text-open")
  )
}

const detailsElements = document.querySelectorAll('[data-show-more]')
detailsElements.forEach((element) => element.addEventListener('toggle', () => handleToggle(element)))
