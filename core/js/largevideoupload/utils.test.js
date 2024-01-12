import {
  isAddVideoPage,
  isEditVideoPage,
  showHideElements,
  createElement,
  isFormValid,
  scrollToTopOfPage,
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

  it('isFormValid()', () => {
    let mockFile = new File([new Blob(['xyz'])], 'test-file-name', {
      name: 'test-file-name',
    })

    document.body.innerHTML =
      '<div>' +
      '<div class="messages"></div>' +
      '  <div data-contentpath="title"><div class="w-field__errors"></div><input type"text" id="id_title" /></div>' +
      '  <div data-contentpath="file"><div class="w-field__errors"></div><input type"file" id="id_file" /></div>' +
      '  <div data-contentpath="subtitles_en"><div class="w-field__errors"></div><input type"textarea" id="id_subtitles_en" /></div>' +
      '</div>'

    expect(isFormValid(mockFile)).toBe(false)

    document.querySelector('#id_title').value = 'test title'
    document.querySelector('#id_subtitles_en').value = 'test english subtitles'

    expect(isFormValid(mockFile)).toBe(true)
  })

  it('scrollToTopOfPage()', () => {
    document.body.innerHTML = '<div id="main"></div>'
    const main = document.querySelector('#main')
    main.scrollTo = jest.fn()

    expect(main.scrollTo).toHaveBeenCalledTimes(0)

    scrollToTopOfPage(document)

    expect(main.scrollTo).toHaveBeenCalledTimes(1)
  })
})
