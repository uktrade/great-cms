import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import { HashRouter, Route, Link, Switch, Redirect } from 'react-router-dom'
import Services from '@src/Services'
import { config } from '@src/config'
import ProductSelector from './ProductSelector'
import MarketSelector from './MarketSelector'
import LottieAnimation from '@src/components/Animation/LottieAnimation'
import loaderAnimation from './loader.json'

export function ExportPlanWizard() {
  const [product, setProduct] = useState()
  const [market, setMarket] = useState()
  const [isCreating, setCreating] = useState()
  const creationFakeDelay = 4000

  const paths = { product: '/', market: '/market' }

  const createClick = () => {
    const data = {
      export_commodity_codes: [product],
      export_countries: [market],
    }
    Services.createExportPlan(data).then((result) => {
      // Jump to our newly created EP
      // Todo: error handling here if/when BE does more validation.
      if (result.pk) {
        setCreating(true)
        setTimeout(() => {
          window.location.assign(`${config.apiExportPlanBaseUrl}${result.pk}/`)
        }, creationFakeDelay)
      }
    })
  }

  return (
    <HashRouter>
      <Switch>
        <Route exact path={paths.product}>
          <div class="c-1-4">
            <span class="-section--back-to">
              <a
                href="/export-plan/"
                class="back-link h-m link body-m-b m-t-xs"
              >
                <i class="fas fa-arrow-circle-left"></i>
                <span class="m-f-xs">Back</span>
              </a>
            </span>
          </div>
          <div class="c-1-2 p-t-l">
            <div className="clearfix m-b-m">
              <div className="body-m">Creating exportplan step 1 of 2</div>
              <h2 className="h-m">What are you exporting?</h2>
              <p className="text-blue-deep-80">
                Choose a product to start your plan and get supporting
                information that's tailored to your business.
              </p>
              <ProductSelector valueChange={setProduct} selected={product} />
            </div>
            <div>
              {product && (
                <Link
                  className="button button--primary"
                  to={product ? paths.market : paths.product}
                >
                  Continue
                </Link>
              )}
            </div>
          </div>
        </Route>

        <Route path={paths.market}>
          <div class="c-1-4">
            {!isCreating ? (
              <span class="-section--back-to">
                <a
                  href="/export-plan/"
                  class="back-link h-m link body-m-b m-t-xs"
                >
                  <i class="fas fa-arrow-circle-left"></i>
                  <span class="m-f-xs">Back</span>
                </a>
              </span>
            ) : (
              '&npsp;'
            )}
          </div>
          <div class="c-1-2 p-t-l">
            {!product && <Redirect to={paths.product} />}
            {isCreating ? (
              <>
                <div className="p-b-xl">
                  <div className="clearfix">
                    <div className="f-l" style={{ marginLeft: '-20px' }}>
                      <LottieAnimation
                        clasName="m-f-0"
                        lotti={loaderAnimation}
                        height={30}
                        width={80}
                      />
                    </div>
                  </div>
                  <h1 className="h-s p-t-0">
                    Creating export plan for selling{' '}
                    {product && product.commodity_name} to{' '}
                    {market && market.country_name}
                  </h1>
                </div>
              </>
            ) : (
              <>
                <div className="clearfix m-b-m">
                  <div className="body-m">Creating exportplan step 2 of 2</div>
                  <h2 className="h-m">Where&apos;s your target market?</h2>
                  <p className="text-blue-deep-80">
                    We didn’t find any saved markets. Choose one to start your
                    plan.
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
                      <a href="#" className="link link--underline body-l">
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
                    Create export plan
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
      <ExportPlanWizard />
    </Provider>,
    params.element
  )
}
