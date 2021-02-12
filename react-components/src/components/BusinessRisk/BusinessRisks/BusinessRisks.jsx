import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'

const RadioItem = ({ id, group, value, label, handleOnChange, selected }) => {
  return (
    <div>
      <input
        type="radio"
        name={group}
        id={id}
        value={value}
        onChange={(e) => handleOnChange(id, e)}
        checked={selected === id}
      />
      <label htmlFor={id}>{label}</label>
    </div>
  )
}

const Radiogroup = ({ list }) => {
  const [selected, setSelected] = useState(list.selectedId || null)
  const [radioState, setRadioState] = useState(list)

  const handleOnChange = (id) => {
    setSelected(id)
    setRadioState({ ...radioState, selectedId: selected })
    // console.log(selected);
  }

  return (
    <>
      {radioState.list.map((item) => {
        return (
          <RadioItem
            key={item.id}
            id={item.id}
            group={item.group}
            value={item.value}
            label={item.label}
            selected={selected}
            handleOnChange={handleOnChange}
          />
        )
      })}
    </>
  )
}

export const BusinessRisks = ({ formData, companyexportplan, lesson }) => {
  const [risks, setRisks] = useState(formData)
  // debugger
  const addRisk = () => {
    const newRisk = {}
    newRisk.companyexportplan = companyexportplan
    newRisk.value = ''

    Services.createFundingCreditOption({ ...newRisk })
      .then((data) => setRisks([...risks, data]))
      .catch(() => {})
  }

  const deleteRisk = (id) => {
    Services.deleteFundingCreditOption(id)
      .then(() => {
        setRisks(risks.filter((x) => x.pk !== id))
      })
      .catch(() => {})
  }

  const update = (field, value) => {
    Services.updateFundingCreditOption({ ...field, ...value })
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const onChange = (id, value) => {
    value = { value: value }
    const field = risks.find((x) => x.pk === id)
    field.companyexportplan = companyexportplan
    const updatedRisks = risks.map((x) =>
      x.pk === id ? { ...x, ...value } : x
    )
    setRisks(updatedRisks)
    debounceUpdate(field, value)
  }

  const list = {
    selectedId: 'one',
    list: [
      {
        id: 'one',
        group: 'group',
        value: 'one',
        label: 'Label one',
      },
      {
        id: 'two',
        group: 'group',
        value: 'two',
        label: 'Label two',
      },
      {
        id: 'three',
        group: 'group',
        value: 'three',
        label: 'Label three',
      },
      {
        id: 'four',
        group: 'group',
        value: 'four',
        label: 'Label four',
      },
    ],
  }

  return (
    <>
      <h2 className="h-m m-b-xs">Risks</h2>
      <p>
        Record any risks you think your business may face in the following
        table.
      </p>
      <p>These should be specific risks your business faces when exporting.</p>
      <Learning lesson={lesson} />
      <Radiogroup list={list} />
      {/* <Risks
        formData={risks}
        deleteRisk={deleteRisk}
        onChange={onChange}
        addRisk={addRisk}
      /> */}
    </>
  )
}

// BusinessRisks.propTypes = {
//   formData: PropTypes.arrayOf(
//     PropTypes.shape({
//       companyexportplan: PropTypes.number,
//       pk: PropTypes.number,
//     })
//   ).isRequired,
//   companyexportplan: PropTypes.number.isRequired,
// }

// BusinessRisks.defaultProps = {
//   formData: [],
// }
