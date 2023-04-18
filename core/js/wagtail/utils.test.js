import {
  isAddVideoPage,
  isEditVideoPage,
  showHideElements,
  createElement,
} from './utils'

describe('Wagtail utils', () => {
  it('isAddVideoPage()', () => {
    expect(isAddVideoPage('/admin/media/video/add/')).toEqual(true)
    expect(isAddVideoPage('/admin/media/image/add/')).toEqual(false)
  })

  it('isEditVideoPage()', () => {
    expect(isEditVideoPage('/admin/media/edit/101/')).toEqual(true)
    expect(isEditVideoPage('/admin/media/something-else/101/')).toEqual(false)
  })

  it('showHideElements()', () => {
    document.body.innerHTML =
      '<div>' +
      '  <div id="show">show me</div>' +
      '  <div id="hide">hide me</div>' +
      '</div>'

    showHideElements('#show', '#hide')

    expect(document.querySelector('#show').style.display).toEqual('block')
    expect(document.querySelector('#hide').style.display).toEqual('none')

    showHideElements('#hide', '#show')

    expect(document.querySelector('#show').style.display).toEqual('none')
    expect(document.querySelector('#hide').style.display).toEqual('block')
  })

  it('createElement()', () => {
    const testDiv = createElement('div', [
      { key: 'id', val: 'test_div' },
      { key: 'innerHTML', val: 'Test div' },
    ])

    expect(testDiv.id).toEqual('test_div')
    expect(testDiv.innerHTML).toEqual('Test div')
  })
})
