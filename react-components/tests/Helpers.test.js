import {
  dateFormat,
  slugify,
  addItemToList,
  capitalize,
  isObject,
  get,
  mapArray,
  getValue,
  getLabel,
  formatLessonLearned,
  normaliseValues,
  listJoin,
  millify,
  stripPercentage,
  getLabels,
  getValues,
  objectHasValue,
  deepAssign,
  camelize,
  camelizeObject,
  numberWithSign,
  validation,
  sortBy,
  sortMapBy,
} from '@src/Helpers'

const { twoDecimal, wholeNumber, onlyOneZero } = validation

test('slugify', (done) => {
  const testStrings = [
    'Aerospace',
    'Advanced manufacturing',
    'Airports',
    'Agriculture, horticulture and fisheries',
  ]
  const expected = [
    'aerospace',
    'advanced-manufacturing',
    'airports',
    'agriculture-horticulture-and-fisheries',
  ]

  testStrings.forEach((string, i) => {
    expect(slugify(string)).toEqual(expected[i])
  })

  done()
})

describe('addItemToList', () => {
  describe('One field', () => {
    it('Should 1 item', () => {
      expect(addItemToList([], 0, { one: 'item one' })).toEqual([
        { one: 'item one' },
      ])
    })

    it('Should 1 updated item', () => {
      expect(
        addItemToList([{ one: 'item one' }], 0, { one: 'item updated' })
      ).toEqual([{ one: 'item updated' }])
    })

    it('Should 2 items', () => {
      expect(
        addItemToList([{ one: 'item one' }], 0, { two: 'item two' })
      ).toEqual([{ one: 'item one', two: 'item two' }])
    })
  })

  describe('Multiple fields', () => {
    it('Should have 1 item each', () => {
      expect(
        addItemToList([{ one: 'item one' }], 1, { one: 'item one' })
      ).toEqual([{ one: 'item one' }, { one: 'item one' }])
      expect(
        addItemToList([{ one: 'item one' }, { one: 'item one' }], 2, {
          one: 'item one',
        })
      ).toEqual([{ one: 'item one' }, { one: 'item one' }, { one: 'item one' }])
      expect(
        addItemToList(
          [{ one: 'item one' }, { one: 'item one' }, { one: 'item one' }],
          3,
          { one: 'item one' }
        )
      ).toEqual([
        { one: 'item one' },
        { one: 'item one' },
        { one: 'item one' },
        { one: 'item one' },
      ])
    })

    it('Should update second fields, second item', () => {
      const fields = [
        { one: 'item one', two: 'item two' },
        { one: 'item one', two: 'item two' },
        { one: 'item one', two: 'item two' },
      ]
      expect(addItemToList(fields, 1, { two: 'item updated' })).toEqual([
        { one: 'item one', two: 'item two' },
        { one: 'item one', two: 'item updated' },
        { one: 'item one', two: 'item two' },
      ])
    })
  })

  describe('no params', () => {
    expect(addItemToList()).toEqual([{}])
  })
})

test('dateFormat', () => {
  const now = dateFormat()
  expect(dateFormat()).toMatch(now)
  expect(dateFormat('1981-10-15')).toMatch('15 Oct 1981')
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
  expect(isObject(() => 1)).toBeFalsy()
  expect(isObject({})).toBeTruthy()
})

test('get helper', () => {
  const obj = {
    l1: {
      l2: {
        str: 'one-two',
      },
      str: 'one',
    },
  }
  expect(get(obj, 'l1')).toEqual(obj.l1)
  expect(get(obj, 'l1.l2')).toEqual(obj.l1.l2)
  expect(get(obj, 'l1.l2.str')).toEqual(obj.l1.l2.str)
  expect(get(obj, 'l1.l2.bibble')).toBeFalsy()
  expect(get(null, 'l1')).toBeFalsy()
})

test('mapArray', () => {
  const arr = [
    {
      keyVal: 'keyOne',
      name: 'Object 1',
    },
    {
      keyVal: 'keyTwo',
      name: 'value2',
    },
  ]
  const result = mapArray(arr, 'keyVal')
  expect(result.keyOne).toEqual(arr[0])
  expect(result.keyTwo.name).toEqual('value2')
})

describe('Number formats', () => {
  it('normaliseValues', () => {
    ;[
      { str: '123', dp: 1, expect: ['123'] },
      { str: '123.4556', dp: 1, expect: ['123.5'] },
      { str: '123.4556', dp: 2, expect: ['123.46'] },
      { str: '123.4556', dp: 0, expect: ['123'] },
      { str: null, dp: 0, expect: 'Data not available' },
      { str: '0', dp: 0, expect: ['0'] },
      { str: '-1', dp: 0, expect: ['-1'] },
    ].forEach((test) => {
      expect(normaliseValues(test.str, test.dp)).toEqual(test.expect)
    })
  })
  it('millify', () => {
    ;[
      { num: 123, dp: 1, expect: '123' },
      { num: 123456, dp: 1, expect: '123,456' },
      { num: 1234567, dp: 1, expect: '1.2 million' },
      { num: 1000000, dp: 1, expect: '1.0 million' },
      { num: 1555555555, dp: 1, expect: '1.6 billion' },
      { num: 2444444444444, dp: 1, expect: '2.4 trillion' },
      { num: 0, dp: 1, expect: '0' },
      { num: null, dp: 1, expect: null },
    ].forEach((test) => {
      expect(millify(test.num)).toEqual(test.expect)
    })
  })
  it('stripPercentage', () => {
    ;[
      { str: 'country1', expect: 'country' },
      { str: 'country.1', expect: 'country' },
      { str: 'country1.2', expect: 'country' },
      { str: 'country1.23', expect: 'country' },
      { str: 'country 1', expect: 'country' },
      { str: 'country .1', expect: 'country' },
      { str: 'country 1.2', expect: 'country' },
      { str: 'country 1.23', expect: 'country' },
      { str: 'country .1', expect: 'country' },
      { str: 'country 1.2', expect: 'country' },
      { str: 'country 1.23', expect: 'country' },
      { str: 'country1%', expect: 'country' },
      { str: 'country.1%', expect: 'country' },
      { str: 'country1.2%', expect: 'country' },
      { str: 'country1.23%', expect: 'country' },
      { str: 'country 1%', expect: 'country' },
      { str: 'country .1%', expect: 'country' },
      { str: 'country 1.2%', expect: 'country' },
      { str: 'country 1.23%', expect: 'country' },
      { str: 'country .1%', expect: 'country' },
      { str: 'country 1.2%', expect: 'country' },
      { str: 'country 1.23%', expect: 'country' },
      { str: 'country>1%', expect: 'country' },
      { str: 'country <.1%', expect: 'country' },
      { str: 'country >1.2%', expect: 'country' },
      { str: 'country <1.23%', expect: 'country' },
      { str: 'country >.1%', expect: 'country' },
      { str: 'country <1.2%', expect: 'country' },
      { str: 'country >1.23%', expect: 'country' },
      { str: null, expect: null },
    ].forEach((test) => {
      expect(stripPercentage(test.str)).toEqual(test.expect)
    })
  })
})

describe('listJoin', () => {
  it('Should format a list',() => {
    expect(listJoin([])).toEqual('')
    expect(listJoin(['one'])).toEqual('one')
    expect(listJoin(['one','two'])).toEqual('one and two')
    expect(listJoin(['one','two', 'three'])).toEqual('one, two and three')
  })
})

describe('formatLessonLearned', () => {
  const lesson = {
    'managing-exchange-rates': {
      category: 'Exchange rates and moving money',
      title: 'Managing exchange rates',
      duration: '4 min',
      url:
        '/learn/categories/funding-financing-and-getting-paid/exchange-rates-and-moving-money/managing-exchange-rates/',
    },
  }

  const section = {
    lessons: ['managing-exchange-rates', 'another-lesson'],
    url: '/back-to',
  }

  it('Should return a lesson', () => {
    expect(formatLessonLearned(lesson, section, 0)).toEqual({
      ...lesson['managing-exchange-rates'],
      url: `${lesson['managing-exchange-rates'].url}?return-link=${section.url}`,
    })
  })

  it('Should have no lesson', () => {
    expect(formatLessonLearned(lesson, section, 1)).toEqual({})
    expect(formatLessonLearned(lesson, { lessons: [] }, 1)).toEqual({})
  })
})

describe('objectHasValue', () => {
  it('Should return false, no values', () => {
    expect(objectHasValue({})).toBeFalsy()
    expect(objectHasValue({ bar: '', foo: '' })).toBeFalsy()
    expect(objectHasValue({ bar: '', foo: null })).toBeFalsy()
  })
  it('Should return true, has values', () => {
    expect(objectHasValue({ bar: 'bar' })).toBeTruthy()
    expect(objectHasValue({ bar: '', foo: 'asdasd' })).toBeTruthy()
  })
})

describe('Utilities ', () => {
  it('Should deepAssign object', () => {
    const obj1 = { one: 1, two: { twoOne: 21, twoTwo: 22 } }
    const obj2 = { three: 3, two: { twoTwo: 'updated', twoThree: 23 } }
    const obj = deepAssign(obj1, obj2)
    expect(obj.one).toEqual(1)
    expect(obj.two).toEqual({ twoOne: 21, twoTwo: 'updated', twoThree: 23 })
    expect(obj.three).toEqual(3)
  })
  it('Should camelize a string', () => {
    expect(camelize('one')).toEqual('one')
    expect(camelize('one_two_three')).toEqual('oneTwoThree')
    expect(camelize('')).toEqual('')
  })
  it('Should camelize an object', () => {
    expect(camelizeObject({ one: 1, two_three: 23 })).toEqual({
      one: 1,
      twoThree: 23,
    })
  })
  it('Should render number sign', () => {
    expect(numberWithSign(0)).toEqual('0')
    expect(numberWithSign(-23)).toEqual('-23')
    expect(numberWithSign(23)).toEqual('+23')
    expect(numberWithSign('0')).toEqual('0')
    expect(numberWithSign('-23')).toEqual('-23')
    expect(numberWithSign('23')).toEqual('+23')
    expect(numberWithSign('Data not available')).toEqual('Data not available')
  })

  it('Should sort based on a key', () => {
    expect(sortBy([{ key:'zz' },{ key:'a' },{ key:'AA' },{ key:'Z' } ], 'key')).toEqual(
     [{ key:'a' },{ key:'AA' },{ key:'Z' },{ key:'zz' } ])
  })

  it('Should build a sort map based on a key', () => {
    expect(sortMapBy([{ key:'zz' },{ key:'a' },{ key:'AA' },{ key:'Z' } ], 'key')).toEqual(
     [1,2,3,0])
  })
})

describe('Validation', () => {
  describe('twoDecimal', () => {
    it.each`
      a          | expected
      ${2}       | ${true}
      ${0}       | ${true}
      ${'0'}     | ${true}
      ${'2.00'}  | ${true}
      ${'2.21'}  | ${true}
      ${'22.21'} | ${true}
      ${'0.50'}  | ${true}
      ${'0.01'}  | ${true}
      ${6666666} | ${true}
      ${200}     | ${true}
    `('Should be valid - $a', ({ a, expected }) => {
      expect(twoDecimal(a)).toEqual(expected)
    })
    it.each`
      a            | expected
      ${1.5033}    | ${false}
      ${'1.000'}   | ${false}
      ${'33.3333'} | ${false}
    `('Should be invalid - $a', ({ a, expected }) => {
      expect(twoDecimal(a)).toEqual(expected)
    })
  })
  describe('wholeNumber', () => {
    it.each`
      a          | expected
      ${2}       | ${true}
      ${0}       | ${true}
      ${'0'}     | ${true}
      ${'200'}   | ${true}
      ${'2221'}  | ${true}
      ${6666666} | ${true}
      ${200}     | ${true}
    `('Should be valid - $a', ({ a, expected }) => {
      expect(wholeNumber(a)).toEqual(expected)
    })
    it.each`
      a            | expected
      ${1.1}       | ${false}
      ${1.5033}    | ${false}
      ${'1.000'}   | ${false}
      ${'33.3333'} | ${false}
    `('Should be invalid - $a', ({ a, expected }) => {
      expect(wholeNumber(a)).toEqual(expected)
    })
  })
  describe('onlyOneZero', () => {
    it.each`
      a    | b      | expected
      ${0} | ${'0'} | ${true}
    `('Should be invalid - $a and $b', ({ a, b, expected }) => {
      expect(onlyOneZero(a, b)).toEqual(expected)
    })
    it.each`
      a    | b       | expected
      ${0} | ${'1'}  | ${false}
      ${0} | ${'.'}  | ${false}
      ${0} | ${'22'} | ${false}
      ${1} | ${'0'}  | ${false}
      ${1} | ${'30'} | ${false}
    `('Should be valid - $a and $b', ({ a, b, expected }) => {
      expect(onlyOneZero(a, b)).toEqual(expected)
    })
  })
})
