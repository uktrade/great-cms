module.exports = {
  module: {
    rules: [
      {
        test: /\.svg$/,
        loader: 'svg-inline-loader',
        options: {
          removeTags: true,
          removingTags: ['title', 'desc'],
          removeSVGTagAttrs: false,
          removingTagAttrs: ['fill'],
        },
      },
      {
        test: /\.scss$/,
        use: ['css-loader', 'sass-loader'],
      },
      {
        test: /\.css$/,
        use: ['css-loader'],
      },
    ],
  },
}
