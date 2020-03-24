import React from 'react'
import ReactDOM from 'react-dom'
import ButtonAsLink from './ButtonAsLink'
import './stylesheets/Learn.scss'

const Learn = () => (
    <div className="learn-wrapper">
        <h1 className="h1">Start exporting today</h1>
        <p className="paragraph">Start your exporting journey today, and in no time, you’ll have your realistic business plan for selling overseas.</p>
        <ButtonAsLink location="/learn/learn-to-export-step-1">Learn how to export</ButtonAsLink>
    </div>
);

export { Learn }
export default () => ReactDOM.render(<Learn />, document.getElementById('learn-root'))
