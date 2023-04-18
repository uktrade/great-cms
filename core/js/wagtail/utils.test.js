import { isAddVideoPage, isEditVideoPage } from './utils'

describe('Wagtail utils', () => {
  it('isAddVideoPage()', () => {
    expect(isAddVideoPage('/admin/media/video/add/')).toEqual(true)
    expect(isAddVideoPage('/admin/media/image/add/')).toEqual(false)
  })

  it('isEditVideoPage()', () => {
    expect(isEditVideoPage('/admin/media/edit/101/')).toEqual(true)
    expect(isEditVideoPage('/admin/media/something-else/101/')).toEqual(false)
  })
})
