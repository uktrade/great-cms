export function modifyAnchorLinkFormLabel() {
  function isEditPage() {
    const currentPageUrl = window.location.pathname;
    const editPagePattern = /^\/admin\/pages\/\d+\/edit\/$/;
    return editPagePattern.test(currentPageUrl);
  }

  function replaceOldLabelWithNew(element) {
    const newLabel = '# Paste or type anchor identifier name'
    if (element.textContent !== newLabel) {
      element.textContent = newLabel;
    }
  }

  function observeAnchorLabelAndReplace() {
    const anchorLabelId = 'id_anchor-link-chooser-url-label';

    function isAnchorLabelPresent() {
      return document.getElementById(anchorLabelId);
    }

    const observer = new MutationObserver((mutationsList) => {
      const anchorElement = isAnchorLabelPresent();
      if (anchorElement) {
        replaceOldLabelWithNew(anchorElement);
      }
    });

    if (!isAnchorLabelPresent()) {
      // If the label is not present, start observing
      observer.observe(document, { childList: true, subtree: true });
    }
  }

  if (isEditPage()) {
    observeAnchorLabelAndReplace();
  }
}
