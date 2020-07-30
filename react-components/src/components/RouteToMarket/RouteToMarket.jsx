import React from 'react'
import ReactDOM from 'react-dom'
import './RouteToMarket.scss'

function renderTable({ route, promote, why }, index, updateTable) {
  return (
    <div className="route-to-market__table" key={`table_${index}`}>
      <div className="route-to-market__table-cell">
        <label>Route to market</label>
        <input type="text" value={route} onChange={(event) => updateTable(index, 'route', event.target.value)} />
      </div>
      <div className="route-to-market__table-cell">
        <label>How will you promote your product?</label>
        <input type="text" value={promote} onChange={(event) => updateTable(index, 'promote', event.target.value)} />
      </div>
      <div className="route-to-market__table-cell">
        <label>Explain in your words why you selected this route to market and promotional channel</label>
        <input type="text" value={why} onChange={(event) => updateTable(index, 'why', event.target.value)} />
      </div>
    </div>
  )
}

class RouteToMarket extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      tables: []
    }
  }

  addTable = () => {
    this.setState({
      tables: [
        ...this.state.tables,
        {
          route: '',
          promote: '',
          why: ''
        }
      ]
    })
  }

  updateTable = (index, key, value) => {
    const newState = this.state.tables

    newState[index] = {
      ...newState[index],
      [key]: value
    }

    this.setState({
      tables: newState
    })
  }

  render() {
    const {
      state: { tables },
      addTable,
      updateTable
    } = this

    console.log(this.state.tables)

    return (
      <div>
        {tables.length >= 1 && tables.map((props, index) => renderTable(props, index, updateTable))}
        <button onClick={addTable}>Add route to market</button>
      </div>
    )
  }
}

function createRouteToMarket({ element }) {
  ReactDOM.render(<RouteToMarket />, element)
}

export { RouteToMarket, createRouteToMarket }
