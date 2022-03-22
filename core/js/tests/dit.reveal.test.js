require('../src/dit.reveal')

describe('reveal', () => {
  beforeEach(async () => {
    document.body.innerHTML = `
            <button id='toggle' data-reveal-button aria-controls='content'>Toggle content 1</button>
            <div id='content'>Content 1</div>
            <button id='toggle2' data-reveal-button aria-controls='content2'>Toggle content 2</button>
            <div id='content2'>Content 2</div>
        `
    window.document.dispatchEvent(
      new Event('DOMContentLoaded', {
        bubbles: true,
        cancelable: true,
      })
    )
  })

  it('sets up the components', () => {
    expect(
      document.getElementById('toggle').getAttribute('aria-expanded')
    ).toEqual('false')
    expect(
      document.getElementById('content').getAttribute('aria-expanded')
    ).toEqual('false')
  })

  it('expands the linked content on click', () => {
    const button = document.getElementById('toggle')
    const content = document.getElementById('content')

    button.click()

    expect(button.getAttribute('aria-expanded')).toEqual('true')
    expect(content.getAttribute('aria-expanded')).toEqual('true')
    expect(
      document.getElementById('toggle2').getAttribute('aria-expanded')
    ).toEqual('false')
    expect(
      document.getElementById('content2').getAttribute('aria-expanded')
    ).toEqual('false')
  })
})
