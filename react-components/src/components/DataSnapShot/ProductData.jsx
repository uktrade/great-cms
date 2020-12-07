/* eslint-disable import/prefer-default-export */
import React from 'react'
import { Stats } from '@src/components/Stats'

export const ProductData = () => (
  <>
    <div className="grid">
      <div className="c-1-3-l c-1-1-m">
        <Stats header="Total product import value in 2018 (USD)" data="47.7 million" />
      </div>
      <div className="c-1-3-l c-1-1-m">
        <Stats header="Total product import value from the UK in 2018 (USD)" data="11.0 million" />
      </div>
      <div className="c-1-3-l c-1-1-m">
        <Stats header="Year-to-year product import value change" data="+25.1%" />
      </div>
    </div>

    <div className="grid">
      <div className="c-1-2">
        <Stats header="GDP per capita (USD)" data="53,024" />
      </div>
      <div className="c-1-2">
        <Stats header="Avg income (USD)" data="40,291" />
      </div>
    </div>
    <hr className="hr bg-blue-deep-20 m-t-0" />
  </>
)
