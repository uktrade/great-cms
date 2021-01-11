/**
 * Extracted from simplemde source:
 * https://github.com/sparksuite/simplemde-markdown-editor/blob/6abda7ab68cc20f4aca870eb243747951b90ab04/src/js/simplemde.js#L791-L822
 */
function _replaceSelection(cm, active, startEnd, url) {
    if (
        /editor-preview-active/.test(cm.getWrapperElement().lastChild.className)
    )
        return;

    var text;
    var start = startEnd[0];
    var end = startEnd[1];
    var startPoint = cm.getCursor('start');
    var endPoint = cm.getCursor('end');
    if (url) {
        end = end.replace('#url#', url);
    }
    if (active) {
        text = cm.getLine(startPoint.line);
        start = text.slice(0, startPoint.ch);
        end = text.slice(startPoint.ch);
        cm.replaceRange(start + end, {
            line: startPoint.line,
            ch: 0,
        });
    } else {
        text = cm.getSelection();
        cm.replaceSelection(start + text + end);

        startPoint.ch += start.length;
        if (startPoint !== endPoint) {
            endPoint.ch += start.length;
        }
    }
    cm.setSelection(startPoint, endPoint);
}

function onLinkChosen(mde, data) {
    var cm = mde.codemirror;

    if (data.prefer_this_title_as_link_text) {
        // Override the whole selection with link text + URL from the chooser.
        cm.replaceSelection('[' + data.title + '](' + data.url + ')');
    } else {
        var isPageLink = !!data.slug;
        var url = isPageLink ? 'slug:' + data.slug : data.url;
        _replaceSelection(cm, mde.getState().link, ['[', '](#url#)'], url);
    }
}

function openLinkChooser(mde) {
    var cm = mde.codemirror;

    var workflow = window.ModalWorkflow({
        url: window.chooserUrls.pageChooser,
        urlParams: {
            page_type: 'wagtailcore.page',
            allow_external_link: true,
            allow_email_link: true,
            link_text: cm.getSelection(),
        },
        onload: window.PAGE_CHOOSER_MODAL_ONLOAD_HANDLERS,
        responses: {
            pageChosen: function(data) {
                onLinkChosen(mde, data);
                workflow.close();
            },
        },
        onError: function() {
            window.alert('Uh-oh, the link chooser failed to open. Please refresh the page and try again.');
        },
    });
}

// Override window.prompt to integrate with SimpleMDE.
// This is the only way to integrate with SimpleMDE’s link picker
// without actually rewriting SimpleMDE itself.
var windowPrompt = window.prompt;
window.prompt = windowPromptOverride;

function windowPromptOverride(value) {
    // Only override if window.prompt is called with a SimpleMDE instance.
    var isOverride = value instanceof SimpleMDE;

    if (isOverride) {
        openLinkChooser(value);
        return;
    } else {
        return windowPrompt(value);
    }
}

function simplemdeAttach(id) {
    var mde = new SimpleMDE({
        element: document.getElementById(id),
        promptURLs: true,
        autofocus: false,
    });
    mde.options.promptTexts = {
        // We pass the editor instance as the prompt text for links in order to:
        // - Override window.prompt in the appropriate scenarios.
        // - Have access to the editor instance in our custom link chooser.
        link: mde,
    };
    mde.render();

    mde.codemirror.on('change', function() {
        $('#' + id).val(mde.value());
    });
}

// Refresh the markdown entry field when the tab buttons are clicked.
// This works around a problem where CodeMirror cannot determine it's height
// if it is hidden. Tab contents are of course hidden before they are clicked.
// Unless this is done the markdown entry field will appear empty until clicked.
(function() {
    var checkExist = setInterval(function() {
        if (document.getElementsByClassName('tab-nav')) {
            clearInterval(checkExist);
            $('.tab-nav').on('shown.bs.tab', refreshMarkdownFields);
        }
    }, 100);

    function refreshMarkdownFields(event) {
        var id = event.target.getAttribute('href').replace('#', '');
        var tabContent = document.getElementById(id);
        var codeElements = tabContent.getElementsByClassName('CodeMirror');
        for (var j = 0; j < codeElements.length; j++) {
            var codeElement = codeElements[j];
            codeElement.CodeMirror.refresh();
        }
    }
})();
