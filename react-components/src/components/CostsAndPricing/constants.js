export const direct = [
  { label: 'Product cost', id: 'product', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Labour cost', id: 'labour', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Additional margin', id: 'additional_margin', placeholder: 0, tooltip: 'tooltip', type: 'number' }
]

export const overhead = [
  { label: 'Product adaptation', id: 'adaptation', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Packaging and labelling', id: 'packaging', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Freight and logistics', id: 'freight', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Agent and distributor fees', id: 'agent', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Marketing', id: 'marketing', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Insurance', id: 'insurance', placeholder: 0, tooltip: 'tooltip', type: 'number' },
  { label: 'Other overhead costs', id: 'other_overhead', placeholder: 0, tooltip: 'tooltip', type: 'number' }
]

export const costPerUnit = {
  label: 'Cost per unit',
  id: 'cost_per_unit',
  placeholder: 0,
  type: 'number',
  description: '<h2 class="h-xs p-t-0 p-b-0">Your final cost per unit</h2><p class="m-t-xs">Your final cost per unit is how much it costs your business to create one unit of your product.</p><p>To work this out you will need to use 3 pieces of information you recorded earlier:</p><ul class="list-dot"><li>how many units of your product you want to export</li><li>your direct costs final total</li><li>your overhead costs final total</li></ul><p class="m-b-0">You will then be able to calculate this using the tool in the next section.</p>',
  example: '<p class="m-b-0 m-t-xs">For the first step you must divide your overhead costs total by the number of units you are exporting. You must then add this total you have just worked out to your direct cost total you worked out in the table earlier.</p><p class="m-b-0">Input these into the following tool:</p><p class="m-v-0">0 + (0 / 0)</p>'
}

export const averagePrice = {
  label: 'Average Price',
  id: 'average_price',
  tooltip: 'tooltip',
  placeholder: 0,
  type: 'number'
}

export const netPrice = {
  label: 'Net Price',
  id: 'net_price',
  tooltip: 'tooltip',
  type: 'number',
  placeholder: 0,
  example:'<p>To decide a final price for Dove gin we thought about:</p><ul><li>how much it cost to make one bottle of our gin</li><li>the average price for a bottle of gin in Australia</li></ul><p>This helped us decide where our product would sit in the market.</p><p>A bottle of our gin costs £15 to make, so to make a profit we had to charge over £15. Looking at Australian prices we decided on £25 a bottle in line with the market prices there. This gives us a profit margin of £10 on every unit sold.</p>'
}

export const localTaxes = {
  label: 'local Taxes',
  id: 'local_taxes',
  tooltip: 'tooltip',
  type: 'number',
  placeholder: 0,
  example:'<p>Value added tax (VAT) standard rate: 21%</p><p>Value added tax (VAT) reduced rate: 6%</p>'
}

export const duty = {
  label: 'Duty',
  id: 'duty',
  tooltip: 'tooltip',
  type: 'number',
  placeholder: 0,
  example:'<p>Value added tax (VAT) standard rate: 21%</p><p>Value added tax (VAT) reduced rate: 6%</p>',
  description: '<h2 class="h-xs p-t-0 p-b-0">Duty per unit</h2><p class="m-t-xs m-b-0">The Withdrawal Agreement between the EU and the UK entered into force on 1 February 2020. The UK has entered a transition period until 31 December 2020. During the transition period, there will continue to be no duty charged on UK exports by EU member states.</p>'
}

export const unitsToExport = {
  label: 'Number of units to exports',
  id: 'units_to_export',
  placeholder: 0,
  type: 'number'
}

export const exportUnits = {
  id: 'export_units',
  label: 'select unit',
  name: 'select units',
  placeholder: 'Select unit',
  options: [
    {value: 'metre', label: 'metre (s)'},
    {value: 'gram', label: 'gram (s)'},
    {value: 'kilogram', label: 'kilogram (s)'},
    {value: 'piece', label: 'piece (s)'},
    {value: 'set', label: 'set (s)'},
    {value: 'pack', label: 'pack (s)'}
  ]
}

export const grossPriceCurrency = {
  label: 'Gross Price currency',
  id: 'gross_price_per_unit_invoicing',
  tooltip: 'tooltip',
  placeholder: 0,
  type: 'number'
}

export const grossPriceUnitSelect = {
  id: 'gross_price_per_unit_currency',
  label: 'select unit',
  name: 'select units',
  placeholder: 'Select unit',
  options: [{value: 'item_one', label: 'item one'}, {value: 'item_two', label: 'item two'}]
}
