import { updateField, UPDATE_FIELD } from '.'

describe('Costs and Pricing Actions', () => {
  describe('updateField', () => {
    const field = { product: 'tea'}
    it('Should return updated field', () => {
      expect(updateField(field)).toEqual({
        type: UPDATE_FIELD,
        payload: field
      })
    })
  })
})
