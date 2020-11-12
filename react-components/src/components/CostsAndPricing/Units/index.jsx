import React from 'react'
import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'

export const Units = () => {
  return (
    <>
      <h2 className='h-xs p-t-l p-b-0'>Total costs and price</h2>
      <p>Now you have calculated your direct and overhead costs, you can calculate your final cost per unit. This can be
        tricky but don't worry, we will tell you what you need to do.</p>

      <h2 className='h-xs p-t-l p-b-0'>Number of units you want to export</h2>
      <p>The first thing you can do is record how many units of your product you want to export in the following
        tool.</p>
      <p>Try to be as accurate as possible, this will help make your plan stronger.</p>
      <div className='c-1-6 m-r-xs'>
        <Input label='number of units' hideLabel />
      </div>
      <div className='c-1-3'>
        <Select label='select unit' update={() => {}} name='test' options={[]} hideLabel />
      </div>
    </>
  )
}
