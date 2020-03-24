import React from 'react'
import { node, string } from 'prop-types'
import'./stylesheets/ButtonAsLink.scss'

const ButtonAsLink = ({ children, location }) => (
    <a className="buttonAsLink" href={location}>{children}</a>
)

ButtonAsLink.propTypes = {
    children: node.isRequired,
    location: string.isRequired,
}

export default ButtonAsLink
