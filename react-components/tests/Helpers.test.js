import { slugify, addItemToList, capitalize, isObject, get } from '@src/Helpers'

test('slugify', (done) => {
  const testStrings = ['Aerospace', 'Advanced manufacturing', 'Airports', 'Agriculture, horticulture and fisheries']
  const expected = ['aerospace', 'advanced-manufacturing', 'airports', 'agriculture-horticulture-and-fisheries']

  testStrings.forEach((string, i) => {
    expect(slugify(string)).toEqual(expected[i])
  })

  done()
})

describe('addItemToList', () => {

  describe('One field', () => {
    it('Should 1 item', () => {
      expect(addItemToList([], 0, {'one': 'item one'})).toEqual([
        {'one': 'item one'}
      ])
    })

    it('Should 1 updated item', () => {
      expect(addItemToList([{'one': 'item one'}], 0, {'one': 'item updated'})).toEqual([
        {'one': 'item updated'}
      ])
    })

    it('Should 2 items', () => {
      expect(addItemToList([{'one': 'item one'}], 0, {'two': 'item two'})).toEqual([
        {'one': 'item one', 'two': 'item two'},
      ])
    })
  })


  describe('Multiple fields', () => {
    it('Should have 1 item each', () => {
      expect(addItemToList([{'one': 'item one'}], 1, {'one': 'item one'})).toEqual([
        {'one': 'item one'},
        {'one': 'item one'}
      ])
      expect(addItemToList([{'one': 'item one'}, {'one': 'item one'}], 2, {'one': 'item one'})).toEqual([
        {'one': 'item one'},
        {'one': 'item one'},
        {'one': 'item one'}
      ])
      expect(addItemToList([{'one': 'item one'}, {'one': 'item one'}, {'one': 'item one'}], 3, {'one': 'item one'})).toEqual([
        {'one': 'item one'},
        {'one': 'item one'},
        {'one': 'item one'},
        {'one': 'item one'}
      ])
    })

    it('Should update second fields, second item', () => {
      const fields = [
        {'one': 'item one', 'two': 'item two'},
        {'one': 'item one', 'two': 'item two'},
        {'one': 'item one', 'two': 'item two'}
      ]
      expect(addItemToList(fields, 1, {'two': 'item updated'})).toEqual([
        {'one': 'item one', 'two': 'item two'},
        {'one': 'item one', 'two': 'item updated'},
        {'one': 'item one', 'two': 'item two'}
      ])
    })
  })

  describe('no params', () => {
    expect(addItemToList()).toEqual([{}])
  })


})

test('capitalize', () => {
  expect(capitalize('one_two_three')).toMatch('One two three')
  expect(capitalize('one_two_three', false)).toMatch('one two three')
})

test('isObject', () => {
  expect(isObject([])).toBeFalsy()
  expect(isObject('')).toBeFalsy()
  expect(isObject(undefined)).toBeFalsy()
  expect(isObject(null)).toBeFalsy()
  expect(isObject(()=>1)).toBeFalsy()
  expect(isObject({})).toBeTruthy()
})

test('get helper', () => {
  let obj = {
    l1:{
      l2: {
        str:'one-two'
      },
      str:'one'
    }
  }
  expect(get(obj,'l1')).toEqual(obj.l1)
  expect(get(obj,'l1.l2')).toEqual(obj.l1.l2)
  expect(get(obj,'l1.l2.str')).toEqual(obj.l1.l2.str)
  expect(get(obj,'l1.l2.bibble')).toBeFalsy()
  expect(get(null,'l1')).toBeFalsy()
})