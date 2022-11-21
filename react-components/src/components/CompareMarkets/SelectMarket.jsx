import React from 'react'
import ReactHtmlParser from 'react-html-parser'

import {
  useComparisonMarkets,
  useUserMarkets
} from '@src/components/hooks/useUserData'

export default function SelectMarket() {
  const [ comparisonMarkets ] = useComparisonMarkets()
  const { markets } = useUserMarkets()

  const marketSelected = !!markets.filter((market) => market.country_iso2_code in comparisonMarkets).length

  return marketSelected && (
    <section className="next-steps p-h-xl p-v-s m-t-s">
      <h3 className="p-t-0 p-b-xs">Next steps</h3>
      <div className="flex-grid">
        {ReactHtmlParser(document.getElementById('next-steps').innerHTML)}
      </div>
    </section>
  )
}
