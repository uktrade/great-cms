const path = require('path');

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
        use: ['css-loader', 'resolve-url-loader', 'sass-loader'],
      },
      {
        test: /\.css$/,
        use: ['css-loader'],
      },
      {
        test: /\.(ttf|woff|woff2)$/,
        loader: 'file-loader',
        options: {
            name: '[name].[ext]',
            outputPath: 'fonts',
            context: path.resolve(__dirname, 'design-system'),
        },
      },
      { test: /\.(jpg|png|gif)$/, use: 'url-loader?limit=5000' },
    ],
  },
}
