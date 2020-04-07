import React from "react"

import { shallow } from "enzyme"
import Enzyme from "enzyme"
import Adapter from "enzyme-adapter-react-16"

import ErrorList from "@src/components/ErrorList"

Enzyme.configure({ adapter: new Adapter() })

beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test("ErrorList handles no errors", () => {
  const errors = []
  const component = shallow(<ErrorList errors={errors} />)

  expect(component).toEqual({})
})

test("ErrorList handles one error", () => {
  const errors = ["something went wrong"]
  const component = shallow(<ErrorList errors={errors} className="edie" />)

  expect(
    component.matchesElement(
      <ul className="great-mvp-error-list errorlist edie">
        <li key={0} className="error-message">
          something went wrong
        </li>
      </ul>
    )
  ).toEqual(true)
})

test("ErrorList handles multiple errors", () => {
  const errors = ["something went wrong", "something else went wrong"]
  const component = shallow(<ErrorList errors={errors} className="edie" />)

  expect(
    component.containsMatchingElement(
      <ul className="great-mvp-error-list errorlist edie">
        <li key={0} className="error-message">
          something went wrong
        </li>
        <li key={1} className="error-message">
          something else went wrong
        </li>
      </ul>
    )
  ).toEqual(true)
})
