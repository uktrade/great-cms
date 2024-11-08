import React, { useMemo } from 'react'
import PropTypes from 'prop-types'

function Tab(props) {
	const { label, tabId, onClick, onKeyDown, activeTab, setRef } = props
	const selected = activeTab === tabId
	const modifiedLabel = useMemo(() =>
		label.toLowerCase().split(' ').reduce((acc, s) => {
			return acc += s[0].toUpperCase() + s.substr(1) + ' ';
		}, '').trim(),
		[label])

	return (
		<button
			type="button"
			role="tab"
			id={tabId}
			aria-selected={selected}
			aria-controls={`${tabId}-tab`}
			tabIndex={selected ? '0' : '-1'}
			className={`button tab-list-item ${
				selected ? 'tab-list-active' : ''
			}`}
			onClick={() => onClick(tabId)}
			onKeyDown={onKeyDown}
			ref={setRef}
		>
			{modifiedLabel}
		</button>
	)
}

Tab.propTypes = {
	activeTab: PropTypes.string.isRequired,
	tabId: PropTypes.string.isRequired,
	label: PropTypes.string.isRequired,
	onClick: PropTypes.func.isRequired,
	onKeyDown: PropTypes.func.isRequired,
	setRef: PropTypes.func.isRequired,
}

export default Tab
