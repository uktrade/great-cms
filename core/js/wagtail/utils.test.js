import { isAddVideoPage } from './utils';

describe('Wagtail utils', () => {
    it('isAddVideoPage()', () => {
      expect(isAddVideoPage("/admin/media/video/add/")).toEqual(true);
      expect(isAddVideoPage("/admin/media/image/add/")).toEqual(false);
    })
});
