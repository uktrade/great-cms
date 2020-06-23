import { decorate } from '@storybook/addon-actions'
import { withKnobs, select } from '@storybook/addon-knobs'
import availableIcons from '../../utils/availableIcons'
import textInput from './text-input.mdx'
import './text-input'
import '../icon/icon'

const decoratedAction = decorate([() => ['Click']])
const icons = { none: '', ...availableIcons }

export default {
    title: 'Text Input',
    parameters: {
        docs: { page: textInput },
        decorators: [withKnobs],
        'in-dsm': {
            docFilePath: './text-input.docs.json',
            containerClass: 'sample-code',
            id: '<DSM component container ID>',
        },
    },
}

export const Simple = () => {
    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
            <great-text-input type="text"></great-text-input>
        </div>`
    )
}

export const Search = () => {
    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
            <great-text-input
                type="search"
            >
                <button slot="icon">
                    <great-icon name="magGlass" slot="icon" theme="secondary"></great-icon>
                </button>
            </great-text-input>
        </div>`
    )
}
