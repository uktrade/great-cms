import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import { HashRouter, Route, Link, Switch, Redirect } from 'react-router-dom'
import Services from '@src/Services'
import { config } from '@src/config'
import ProductSelector from './ProductSelector'
import MarketSelector from './MarketSelector'



function ExportPlanWizard() {
  const [product, setProduct] = useState()
  const [market, setMarket] = useState()

  const paths = { product: '/', market: '/market', create: '/create' }

  const createClick = () => {
    const data = {
      export_commodity_codes: [product],
      export_countries: [market],
    }
    Services.createExportPlan(data).then((result) => {
      // Jump to our newly created EP
      // Todo: error handling here when BE does more validation.
      if (result.pk) {
        window.location.assign(`${config.apiExportPlanBaseUrl}${result.pk}/`)
      }
    })
  }

  return (
    <>
      <Switch>
        <Route exact path={paths.product}>
          <div className="clearfix m-b-m">
            <h2 className="h-m">What are you exporting?</h2>
            <ProductSelector valueChange={setProduct} selected={product} />
          </div>
          <div>
            <Link
              className="button button--primary"
              to="market"
              disabled={!product}
            >
              Next
            </Link>
          </div>
        </Route>
        <Route path={paths.market}>
          {!product && <Redirect to={paths.product} />}
          <div className="clearfix m-b-m">
            <h2 className="h-m">Where&apos;s your target market?</h2>
            <MarketSelector valueChange={setMarket} selected={market} />
          </div>
          <Link className="button button--primary" to="final">
            Next
          </Link>
        </Route>
        <Route path={paths.final}>
          {(!product || !market) && <Redirect to={paths.product} />}
          <p className="body-l">
            You are about to create a plan to export{' '}
            <span className="body-l-b">{product && product.commodity_name}</span> to{' '}
            <span className="body-l-b">{market && market.country_name}</span>
          </p>
          <div className="clearfix" />
          <button
            type="button"
            className="button button--primary"
            onClick={createClick}
            disabled={!market}
          >
            Create export plan
          </button>
        </Route>
      </Switch>
    </>
  )
}

export default function createExportPlanWizard({ ...params }) {
  ReactDOM.render(
    <HashRouter>
      <Provider store={Services.store}>
        <ExportPlanWizard />
      </Provider>
    </HashRouter>,
    params.element
  )
}
