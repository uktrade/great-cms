import React, { useState } from 'react'
import { useSelector } from 'react-redux'

import { getEpProduct, getEpMarket } from '@src/reducers'
import Services from '@src/Services'
import { config } from '@src/config'
import { get } from '@src/Helpers'
import { Confirmation } from '@src/components/ConfirmModal/Confirmation'


export default function DeleteButton() {
  const [deleteConfirm, setDeleteConfirm] = useState()
  const product = useSelector((state) => getEpProduct(state))
  const country = useSelector((state) => getEpMarket(state))
  const exportPlan = useSelector((state) => {
    console.log('State', state)
    return state.exportPlan || {}})

  const deletePlan = () => {
    Services.deleteExportPlan()
      .then(() => {
        window.location.assign(config.exportPlanBaseUrl)
      })
      .catch(() => {
        // TODO: add snackbar report once available
      })
  }

  const exportPlanName = (exportPlan) => {
    debugger;
    return exportPlan.name || `export plan for selling ${get(exportPlan,'product.commodity_name')} to ${get(exportPlan,'market.country_name')}`
  }

  return (
    <>
      <button
        className="button button--primary button--small button--full-width button--icon m-b-xs export-plan-delete"
        title="Delete your export plan"
        type="button"
        onClick={() => setDeleteConfirm(true)}
      >
        <i className="fas fa-trash-alt"/>
        Delete plan
      </button>
      {deleteConfirm ? (
        <Confirmation
          title={`Are you sure you want to delete ${exportPlanName(exportPlan)}?`}
          body="All data you entered will be deleted."
          yesLabel="Delete plan"
          yesIcon="fa-trash-alt"
          onYes={deletePlan}
          onNo={() => setDeleteConfirm(false)}
        />
      ) : null}
    </>
  )
}
