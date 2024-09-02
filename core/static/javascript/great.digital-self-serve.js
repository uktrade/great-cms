GreatFrontend = window.GreatFrontend || {}

GreatFrontend.DigitalSelfServe = {
    init: (page_title) => {
        if (GreatFrontend.utils.hasUserConsentedToTracking()) {
            if (localStorage.getItem('dss_user_journey')) {
                localStorage.setItem(
                'dss_user_journey',
                `${localStorage.getItem('dss_user_journey')} > ${page_title}`
                )
            } else {
                localStorage.setItem('dss_user_journey', `${page_title}`)
            }

            document.querySelectorAll('[data-task-item]').forEach(el => {
                el.addEventListener('click', (e) => {
                    const data = el.dataset.task.split('|');

                    window.dataLayer.push({
                        event: 'DEPCardClick',
                        task_id: data[0],
                        task_title: data[1],
                        output_type: data[2],
                        position: data[3]
                    });
                })
            })

            document.querySelectorAll('details').forEach(el => {
                el.addEventListener("mouseleave", (e) => {
                    document.activeElement.blur()
                })
            });

            document.querySelectorAll('details summary').forEach(el => {
                el.addEventListener("click", (e) => {
                    const data = el.dataset.task.split('|');
                    const text = el.querySelector('.govuk-accordion__section-toggle-text').innerText

                    window.dataLayer.push({
                        event: 'DEPCardClick',
                        task_id: data[0],
                        show_or_hide: text,
                    });
                })
            });
        }
    }
}
