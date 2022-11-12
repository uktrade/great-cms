import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useSelector } from 'react-redux'

import { getEpProduct, getEpMarket } from '@src/reducers'
import Services from '@src/Services'
import { config } from '@src/config'
import { Confirmation } from '@src/components/ConfirmModal/Confirmation'
import { analytics, camelizeObject } from '@src/Helpers'

export default function ActionBar({exportPlanProgress}) {

  const { sectionProgress, sectionsCompleted } = camelizeObject(exportPlanProgress)
  const [deleteConfirm, setDeleteConfirm] = useState()
  const product = useSelector((state) => getEpProduct(state))
  const country = useSelector((state) => getEpMarket(state))
  const exportPlan = useSelector((state) => {
    return state.exportPlan || {}
  })
  const analyticsEvent = (eventType) => {
    analytics({
      event: eventType,
      exportPlanMarketSelected: country.country_name,
      exportPlanProductSelected: product.commodity_name,
      exportPlanProductHSCode: product.commodity_code,
      exportPlanSectionsComplete: sectionsCompleted,
      exportPlanFieldsFilled: (sectionProgress || []).reduce(
        (a, section) => a + section.populated,
        0
      ),
    })
  }

  const deletePlan = () => {
    analyticsEvent('deleteExportPlan')
    Services.deleteExportPlan()
      .then(() => {
        window.location.assign(config.exportPlanBaseUrl)
      })
      .catch(() => {
        // TODO: add snackbar report once available
      })
  }

  const downloadPlan = () => {
    analyticsEvent('downloadExportPlan')
    window.location.assign(config.exportPlanDownloadUrl)
  }

  return (
    <>
      <button
        className="button primary-button button--small button--full-width button--icon m-b-xs export-plan-download"
        title="Download your export plan"
        type="button"
        onClick={downloadPlan}
      >
        <i className="fas fa-download" />
        Download plan
      </button>

      <button
<<<<<<< HEAD
        className="button secondary-button delete-button button--small button--full-width button--icon m-b-xs export-plan-delete"
=======
        className="button secondary-button button--small button--full-width button--icon m-b-xs export-plan-delete"
>>>>>>> 177f15c9 (restyled additional pages)
        title="Delete your export plan"
        type="button"
        onClick={() => setDeleteConfirm(true)}
      >
        <i className="fas fa-trash-alt" />
        <span>Delete plan</span>
      </button>
      {deleteConfirm ? (
        <Confirmation
          title={`Are you sure you want to delete ${exportPlan.name}?`}
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

ActionBar.propTypes = {
  exportPlanProgress: PropTypes.shape({
    section_progress: PropTypes.arrayOf(
      PropTypes.shape({
        populated: PropTypes.number,
        total: PropTypes.number,
      })
    ),
    sections_completed: PropTypes.number,
  }).isRequired,
}
