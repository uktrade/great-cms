import React from 'react'
import ReactHtmlParser from 'react-html-parser'

import {
  useComparisonMarkets,
  useUserMarkets
} from '@src/components/hooks/useUserData'

export default function SelectMarket() {
  const [ comparisonMarkets ] = useComparisonMarkets()
  const { markets } = useUserMarkets()

  const marketSelected = markets.filter((market) => market.country_iso2_code in comparisonMarkets).length

  return marketSelected && (
    <section className="bg-red-90 p-h-xl p-v-s m-t-s">
      <h2 className="h-s text-white p-t-0 p-b-xs">Next steps</h2>
      <div className="flex-grid">
        {ReactHtmlParser(document.getElementById('next-steps').innerHTML)}
      </div>
    </section>
  )
}
