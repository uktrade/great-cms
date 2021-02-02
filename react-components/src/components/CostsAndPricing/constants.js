export const direct = [
  {
    label: 'Product cost',
    id: 'product_costs',
    placeholder: '0',
    tooltip: {
      content:
        '<p>These are the costs of the parts, materials or ingredients that go onto making the end product.</p><p>This does not include labour costs.</p>',
      title: 'What are product costs?',
    },
    type: 'number',
    field: 'direct_costs',
  },
  {
    label: 'Labour cost',
    id: 'labour_costs',
    placeholder: '0',
    tooltip: {
      content:
        '<p>These are the costs related to paying wages for employees who work on making your product directly including workers on your assembly line.</p>',
      title: 'What are labour costs?',
    },
    type: 'number',
    field: 'direct_costs',
  },
  {
    label: 'Additional margin',
    id: 'other_direct_costs',
    placeholder: '0',
    tooltip: {},
    type: 'number',
    field: 'direct_costs',
  },
]

export const overhead = [
  {
    label: 'Product adaptation',
    id: 'product_adaption',
    placeholder: '0',
    tooltip: {
      content:
        '<p>These are any changes you need to make to sell abroad. This includes translations, rebranding, packaging and labelling, and meeting local regulations.</p>',
      title: 'What is product adaptation?',
    },
    type: 'number',
    field: 'overhead_costs',
  },
  {
    label: 'Freight and logistics',
    id: 'freight_logistics',
    placeholder: '0',
    tooltip: {
      content:
        '<p>Logistics is the process of getting your goods to their final destination.</p><p>A freight forwarder is a third-party agent that most UK companies use to transport their goods.</p>',
      title: 'What is freight and logistics?',
    },
    type: 'number',
    field: 'overhead_costs',
  },
  {
    label: 'Agent and distributor fees',
    id: 'agent_distributor_fees',
    placeholder: '0',
    tooltip: {
      content:
        '<p>An agent is someone who acts on your behalf to sell your product and a distributor is an independent contractor. They take your product and sell them to the customer with an added margin. Both of which will charge fees for their services.</p>',
      title: 'What are agents and distributor fees?',
    },
    type: 'number',
    field: 'overhead_costs',
  },
  {
    label: 'Marketing',
    id: 'marketing',
    placeholder: '0',
    tooltip: {
      content:
        '<p>This is how you promote your products abroad.</p><p>You can do marketing yourself or pay for marketing services, but either way there will probably be a cost.</p>',
      title: 'What is marketing?',
    },
    type: 'number',
    field: 'overhead_costs',
  },
  {
    label: 'Insurance',
    id: 'insurance',
    placeholder: '0',
    tooltip: {
      content:
        '<p>Like any business activity, exporting has its risks.</p><p>You can minimise these risks by looking at any challenges you might face and deciding whether you should insure against them.</p>',
      title: 'What is insurance?',
    },
    type: 'number',
    field: 'overhead_costs',
  },
  {
    label: 'Other overhead costs',
    id: 'other_overhead_costs',
    placeholder: '0',
    tooltip: {},
    type: 'number',
    field: 'overhead_costs',
  },
]

export const costPerUnit = {
  label: 'Cost per unit',
  id: 'final_cost_per_unit',
  placeholder: '0',
  type: 'number',
  description:
    '<h2 class="h-xs p-t-0 p-b-0">Your final cost per unit</h2><p class="m-t-xs">Your final cost per unit is how much it costs your business to create one unit of your product.</p><p>To work this out you will need:</p><ul class="list-dot"><li>your total direct costs</li><li>your total overhead costs</li><li>the number of units you want to export</li></ul><p class="m-b-0">To help you, we\'ve created an estimate for you based on the figures you gave earlier.</p>',
  example: {
    header: (cost) => `Your estimate cost per unit is ${cost}`,
    buttonTitle: 'Estimate',
    content:
      '<p class="m-b-0">We calculated this by:</p><ul class="list-dot"><li>taking your total overhead costs</li><li>dividing it by the number of units you want to export</li><li>adding this to your direct costs</li></ul><p class="m-v-0">You may want to adjust this estimate, especially if your overhead costs are varied.</p>',
  },
  field: 'total_cost_and_price',
}

export const averagePrice = {
  label: 'Average Price',
  id: 'average_price_per_unit',
  tooltip:
    '<h3>To calculate the average, add the prices together then divide by the number of prices.</h3><p>For example;</p><ul><li>product 1 costs €10</li><li>product 2 costs €12</li><li>product 3 costs €17</li></ul><p>10+12+17=39</p><p>39÷3=13</p><p>Finally, convert €13 into GBP at the current market rate to get the GBP average.</p>',
  placeholder: '0',
  type: 'number',
  field: 'total_cost_and_price',
}

export const netPrice = {
  label: 'Net Price',
  id: 'net_price',
  tooltip: {
    content:
      '<p>This is the price the customer pays for a single unit of your product before taxes have been added to the final price.</p>',
    title: 'What is net price?',
  },
  type: 'number',
  placeholder: '0',
  example: {
    content:
      '<p>To decide a final price for Dove gin we thought about:</p><ul><li>how much it cost to make one bottle of our gin</li><li>the average price for a bottle of gin in Australia</li></ul><p>This helped us decide where our product would sit in the market.</p><p>A bottle of our gin costs £15 to make, so to make a profit we had to charge over £15. Looking at Australian prices we decided on £25 a bottle in line with the market prices there. This gives us a profit margin of £10 on every unit sold.</p>',
  },
  field: 'total_cost_and_price',
}

export const localTaxes = {
  label: 'local Taxes',
  id: 'local_tax_charges',
  tooltip: {
    content:
      "<p>These are the taxes charged by the UK government, the government of your target market, or both.</p><p>In the UK, our local sales tax is called VAT or goods and services tax (GST).</p><p>The rate of tax you pay depends on where you're exporting.</p><p>This means that if you change target country or export to more than one place, you'll need to recalculate your gross price per unit.</p>",
    title: 'What are local sales taxes?',
  },
  type: 'number',
  placeholder: '0',
  example: {
    buttonTitle: 'Local taxes',
    content:
      "<p>The rate of tax you pay depends on where you're exporting to.</p><p>If you change your target country or export to more than one place, you'll need to recalculate your gross price per unit.</p>",
  },
  field: 'total_cost_and_price',
}

export const duty = {
  label: 'Duty',
  id: 'duty_per_unit',
  tooltip:
    '<h3>What are duties?</h3><p>Duties are fees charged by the government of your target market.</p><p>These are designed to keep markets competitive.</p><p>Duties are always charged on goods, while taxes can be charged on people and goods.</p>',
  type: 'number',
  placeholder: '0',
  description:
    '<h2 class="h-xs p-t-0 p-b-0">Duty per unit</h2><p class="m-t-xs m-b-0">To find out which duties and charges you might need to pay, visit Check how to export goods and choose the commodity code that best matches your product.</p>',
  field: 'total_cost_and_price',
}

export const unitsToExport = {
  label: 'Number of units to exports',
  id: 'units_to_export',
  placeholder: '0',
  type: 'number',
  field: (x) => ({
    total_cost_and_price: {
      units_to_export_first_period: x,
    },
  }),
}

export const exportUnits = {
  id: 'export_units',
  label: 'select unit',
  name: 'select units',
  placeholder: 'Select unit',
  field: 'total_cost_and_price',
}

export const timeframe = {
  label: 'Time frame to export',
  id: 'time_frame',
  placeholder: '0',
  type: 'number',
  field: (x) => ({
    total_cost_and_price: {
      units_to_export_second_period: x,
    },
  }),
}

export const timeframeUnits = {
  id: 'export_time_frame',
  label: 'select timeframe',
  name: 'select units',
  placeholder: 'Select unit',
  field: 'total_cost_and_price',
}

export const grossPriceCurrency = {
  label: 'Gross Price currency',
  id: 'gross_price_per_unit_invoicing',
  tooltip: 'tooltip',
  placeholder: '0',
  type: 'number',
  field: (x) => ({
    total_cost_and_price: {
      gross_price_per_unit_invoicing_currency: x,
    },
  }),
}

export const grossPriceUnitSelect = {
  id: 'gross_price_per_unit_currency',
  label: 'select unit',
  name: 'select units',
  placeholder: 'Select unit',
}
