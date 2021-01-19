import React from 'react'
import PropTypes from 'prop-types'

function Tab(props) {
	const { label, onClick, activeTab } = props

	return (
		<button
			type="button"
			className={`tab-list-item m-r-s ${
				activeTab === label ? 'tab-list-active' : ''
			}`}
			onClick={() => onClick(label)}
		>
			{label}
		</button>
	)
}

Tab.propTypes = {
	activeTab: PropTypes.string.isRequired,
	label: PropTypes.string.isRequired,
	onClick: PropTypes.func.isRequired,
}

export default Tab
