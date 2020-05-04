const path = require('path');

module.exports = {
  module: {
    rules: [
      {
        test: /\.svg$/i,
        loader: 'svg-inline-loader',
        options: {
          removeTags: true,
          removingTags: ['title', 'desc'],
          removeSVGTagAttrs: false,
          removingTagAttrs: ['fill'],
        },
      },
      {
        test: /\.scss$/i,
        use: ['css-loader', 'resolve-url-loader', 'sass-loader'],
      },
      {
        test: /\.css$/i,
        use: ['css-loader'],
      },
      {
        test: /\.(ttf|woff|woff2)$/i,
        loader: 'file-loader',
        options: {
            name: '[name].[ext]',
            outputPath: 'fonts',
            context: path.resolve(__dirname, 'design-system'),
        },
      },
      { test: /\.(jpg|png|gif)$/i, use: 'url-loader?limit=5000' },
    ],
  },
}
