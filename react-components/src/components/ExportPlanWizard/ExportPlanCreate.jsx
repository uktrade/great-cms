import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import { HashRouter, Route, Link, Switch, Redirect } from 'react-router-dom'
import Services from '@src/Services'
import { config } from '@src/config'
import ProductSelector from './ProductSelector'
import MarketSelector from './MarketSelector'
import { get } from '@src/Helpers'
import { analytics } from '@src/Helpers'

export function ExportPlanWizard({ exportPlan }) {
  const [product, setProduct] = useState(get(exportPlan, 'export_commodity_codes.0'))
  const [market, setMarket] = useState(get(exportPlan, 'export_countries.0'))
  const [isCreating, setCreating] = useState()
  const creationFakeDelay = 4000

  const paths = { product: '/', market: '/market' }

  const isEditing = !!exportPlan
  const processName = exportPlan
    ? 'Updating export plan'
    : 'Creating export plan'

  const createClick = () => {
    const data = {
      export_commodity_codes: [product],
      export_countries: [market],
    }

    setCreating(true)
    const updateCreate = exportPlan
      ? Services.updateExportPlan
      : Services.createExportPlan

    console.log(data)

    if (Services.createExportPlan) {
      analytics({
        event: 'createExportPlan',
        exportPlanMarketSelected: data.export_countries[0]?.country_name,
        exportPlanProductSelected: data.export_commodity_codes[0]?.commodity_name,
        exportPlanProductHSCode: data.export_commodity_codes[0]?.commodity_code
      })
    }
    updateCreate(data).then((result) => {
      // TODO: error handling here if/when BE does more validation.
      if (result.hashid || exportPlan) {
        setTimeout(() => {
          // Jump to our newly created EP
          const dashboardUrl = result.hashid
            ? `${config.exportPlanBaseUrl}${result.hashid}/`
            : config.exportPlanDashboardUrl
          window.location.assign(dashboardUrl)
        }, creationFakeDelay)
      }

    })
  }

  return (
    <HashRouter>
      <Switch>
        <Route exact path={paths.product}>
          <div className="c-1-4">
            <a
              href={config.exportPlanBaseUrl}
              className="back-link h-m link body-m-b m-t-xs"
            >
              <i className="fas fa-arrow-circle-left" />
              <span className="m-f-xs">Back</span>
            </a>
          </div>
          <div className="c-1-2 p-t-l">
            <div className="clearfix m-b-m">
              <div className="body-m">{processName} step 1 of 2</div>
              <h2 className="h-m">What are you exporting?</h2>
              <p className="text-blue-deep-80">
                Choose a product to start your plan and get supporting
                information that&apos;s tailored to your business.
              </p>
              <ProductSelector valueChange={setProduct} selected={product} />
            </div>
            <div>
              {product && (
                <Link className="button button--primary" to={paths.market}>
                  Continue
                </Link>
              )}
            </div>
          </div>
        </Route>

        <Route path={paths.market}>
          <div className="c-1-4">
            {!isCreating ? (
              <Link
                to={paths.product}
                className="back-link h-m link body-m-b m-t-xs"
              >
                <i className="fas fa-arrow-circle-left" />
                <span className="m-f-xs">Back</span>
              </Link>
            ) : (
              <>&nbsp;</>
            )}
          </div>
          <div className="c-1-2 p-t-l">
            {!product && <Redirect to={paths.product} />}
            {isCreating ? (
              <>
                <div className="p-b-xl m-b-xxl">
                  <div className="wave-animation">
                    <span />
                    <span />
                    <span />
                    <span />
                  </div>
                  <h1 className="h-s p-t-0">
                    {processName} for selling{' '}
                    {product && product.commodity_name} to{' '}
                    {market && market.country_name}
                  </h1>
                </div>
              </>
            ) : (
              <>
                <div className="clearfix m-b-m">
                  <div className="body-m">{processName} step 2 of 2</div>
                  <h2 className="h-m">Where&apos;s your target market?</h2>
                  <p className="text-blue-deep-80">
                    Choose a place to start your plan.
                  </p>
                  <MarketSelector
                    valueChange={setMarket}
                    selected={market}
                    selectedProduct={product}
                  />
                  {!market && (
                    <div className="g-panel m-t-l p-v-m">
                      <div className="body-l-b">
                        Not sure which country to choose?
                      </div>
                      <a
                        href={config.compareCountriesUrl}
                        className="link link--underline body-l"
                      >
                        Find one in “Where to export” service.
                      </a>
                    </div>
                  )}
                </div>
                {market && (
                  <button
                    type="button"
                    className="button button--primary"
                    onClick={createClick}
                  >
                    {exportPlan ? 'Update' : 'Create'} export plan
                  </button>
                )}
              </>
            )}
          </div>
        </Route>
      </Switch>
    </HashRouter>
  )
}

export default function createExportPlanWizard({ ...params }) {
  ReactDOM.render(
    <Provider store={Services.store}>
      <ExportPlanWizard exportPlan={params.exportPlan} />
    </Provider>,
    params.element
  )
}
