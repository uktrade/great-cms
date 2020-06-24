export default ({ self }) =>
    self.getAttributeNames().reduce((accumulator, attribute) => {
        accumulator[attribute] = self.getAttribute(attribute)
        return accumulator
    }, {})
