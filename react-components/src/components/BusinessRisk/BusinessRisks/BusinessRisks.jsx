import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'

const RadioItem = ({ id, group, value, label, onChange, selected }) => {
  return (
    <div className="great-radiogroup__item">
      <input
        className="great-radiogroup__input"
        type="radio"
        name={group}
        id={id}
        value={value}
        onChange={(e) => onChange(id, e)}
        checked={selected === id}
      />
      <label htmlFor={id} className="great-radiogroup__label">
        {label}
      </label>
    </div>
  )
}

const Radiogroup = ({ radioList, className, type, buttonType }) => {
  const [selected, setSelected] = useState(radioList.selectedId || null)
  const [radioState, setRadioState] = useState(radioList)

  const handleOnChange = (id) => {
    setSelected(id)
    setRadioState({ ...radioState, selectedId: selected })
  }

  return (
    <>
      <h3 className="form-label">{radioList.label}</h3>
      <radiogroup
        className={`
          great-radiogroup 
          ${type === 'button' ? 'great-radiogroup--button' : ''}
          ${buttonType === 'temperature' ? 'great-radiogroup--temperature' : ''}
          ${className}
        `}
      >
        {radioState.options.map((item) => {
          return (
            <RadioItem
              key={item.pk}
              id={item.pk}
              group={item.group}
              value={item.value}
              label={item.label}
              selected={selected}
              onChange={handleOnChange}
            />
          )
        })}
      </radiogroup>
    </>
  )
}
Radiogroup.defaultProps = {
  className: 'm-b-xs',
  type: 'button',
  buttonType: 'temperature',
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

  const options_risk_likelihood = {
    selectedId: 4,
    label: 'Risk likelihood',
    options: [
      {
        pk: 1,
        group: 'options_risk_likelihood',
        value: 'rare',
        label: 'Rare',
      },
      {
        pk: 2,
        group: 'options_risk_likelihood',
        value: 'unlikely',
        label: 'Unlikely',
      },
      {
        pk: 3,
        group: 'options_risk_likelihood',
        value: 'possible',
        label: 'Possible',
      },
      {
        pk: 4,
        group: 'options_risk_likelihood',
        value: 'likely',
        label: 'Likely',
      },
      {
        pk: 5,
        group: 'options_risk_likelihood',
        value: 'certain',
        label: 'Certain',
      },
    ],
  }
  const options_risk_impact = {
    selectedId: 8,
    label: 'Risk impact',
    options: [
      {
        pk: 6,
        group: 'options_risk_impact',
        value: 'trivial',
        label: 'Trivial',
      },
      {
        pk: 7,
        group: 'options_risk_impact',
        value: 'minor',
        label: 'Minor',
      },
      {
        pk: 8,
        group: 'options_risk_impact',
        value: 'moderate',
        label: 'Moderate',
      },
      {
        pk: 9,
        group: 'options_risk_impact',
        value: 'major',
        label: 'Major',
      },
      {
        pk: 10,
        group: 'options_risk_impact',
        value: 'severe',
        label: 'Severe',
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
      <Radiogroup radioList={options_risk_likelihood} />
      <Radiogroup radioList={options_risk_impact} />
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
