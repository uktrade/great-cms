// Using webpack's require.context to import all SVGs within /icons folder recursively
// and normalise their names to be exported in ES6

const context = require.context('.', true, /\.svg$/)
// matches word(s) delimited by optional dashes
const regex = /^.\/((?:\w+-?)+)\.svg$/i
const iconNames = context.keys().map((key) =>
    // converts all words to camel case names
    key.replace(regex, (_, p1) =>
        p1
            .split('-')
            .reduce(
                (name, word, i) =>
                    i === 0 ? word.toLowerCase() : `${name}${word[0].toUpperCase()}${word.substr(1).toLowerCase()}`,
                ''
            )
    )
)
const icons = context.keys().reduce((images, path, index) => {
    images[iconNames[index]] = context(path) // eslint-disable-line no-param-reassign
    return images
}, {})

export { iconNames }
export default icons
