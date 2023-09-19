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

  if (isEditPage()) {
    waitForAnchorLabel().then((element) => {
      if (element) {
        replaceOldLabelWithNew(element);
      }
    });
  }
}

function waitForAnchorLabel() {
  return new Promise((resolve) => {
    function isAnchorLabelPresent() {
      return document.getElementById('id_anchor-link-chooser-url-label');
    }

    const observer = new MutationObserver((mutationsList, observer) => {
      const anchorElement = isAnchorLabelPresent();
      if (anchorElement) {
        resolve(anchorElement);
        observer.disconnect();
      }
    });

    observer.observe(document, { childList: true, subtree: true });
  });
}
