import React from 'react'
import PropTypes from 'prop-types'

function Tab(props) {
	const { label, tabId, onClick, activeTab } = props

	return (
		<button
			type="button"
			className={`tab-list-item m-r-s ${
				activeTab === tabId ? 'tab-list-active' : ''
			}`}
			onClick={() => onClick(tabId)}
		>
			{label}
		</button>
	)
}

Tab.propTypes = {
	activeTab: PropTypes.string.isRequired,
	tabId: PropTypes.string.isRequired,
	label: PropTypes.string.isRequired,
	onClick: PropTypes.func.isRequired,
}

export default Tab
