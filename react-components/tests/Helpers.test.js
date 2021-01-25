import {
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
  millify,
} from '@src/Helpers'

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
  let obj = {
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
  let arr = [
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
    [
      {str:'123', dp:1, expect:['123']},
      {str:'123.4556', dp:1, expect:['123.5']},
      {str:'123.4556', dp:2, expect:['123.46']},
      {str:'123.4556', dp:0, expect:['123']},
      {str:null, dp:0, expect:'Data not available'},
      {str:'0', dp:0, expect:['0']},
      {str:'-1', dp:0, expect:['-1']},
    ].forEach((test) => {
      expect(normaliseValues(test.str, test.dp)).toEqual(test.expect)
    })
  })
  it('millify', () => {
    [
      {num:123, dp:1, expect:'123'},
      {num:123456, dp:1, expect:'123,456'},
      {num:1234567, dp:1, expect:'1.2 million'},
      {num:1000000, dp:1, expect:'1.0 million'},
      {num:1555555555, dp:1, expect:'1.6 billion'},
      {num:2444444444444, dp:1, expect:'2.4 trillion'},
      {num:0, dp:1, expect:'0'},
      {num:null, dp:1, expect:null},

    ].forEach((test) => {
      expect(millify(test.num)).toEqual(test.expect)
    })    
  })
})

describe('getLabel', () => {
  it('Should return a label', () => {
    const list = [
      { value: 'd', label: 'days' },
      { value: 'm', label: 'months' },
    ]
    expect(getLabel(list, 'd')).toEqual('days')
  })

  it('Should have no label', () => {
    const list = [
      { value: 'd', label: 'days' },
      { value: 'm', label: 'months' },
    ]
    expect(getLabel(list, 'n')).toEqual('')
    expect(getLabel(list, '')).toEqual('')
  })
})

describe('getValue', () => {
  it('Should return a value', () => {
    const list = [
      { value: 'd', label: 'days' },
      { value: 'm', label: 'months' },
    ]
    expect(getValue(list, 'days')).toEqual('d')
  })

  it('Should have no value', () => {
    const list = [
      { value: 'd', label: 'days' },
      { value: 'm', label: 'months' },
    ]
    expect(getValue(list, 'hour')).toEqual('')
    expect(getValue(list, '')).toEqual('')
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
