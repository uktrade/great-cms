import { slugify } from '@src/Helpers'


test('slugify', done => {
  const testStrings = [
    "Aerospace",
    "Advanced manufacturing",
    "Airports",
    "Agriculture, horticulture and fisheries",
  ]
  const expected = [
    "aerospace",
    "advanced-manufacturing",
    "airports",
    "agriculture-horticulture-and-fisheries",
  ]

  testStrings.forEach((string, i) => {
    expect(slugify(string)).toEqual(expected[i])
  })

  done()

})
