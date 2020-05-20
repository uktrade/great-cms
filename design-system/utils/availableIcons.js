import { iconNames } from '../components/icon/icons'

export default iconNames.reduce((accu, name) => {
    accu[name] = name // eslint-disable-line no-param-reassign
    return accu
}, {})
