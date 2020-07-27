const path = require('path')

module.exports = {
  resolve: {
    modules: ['../', '../node_modules'],
    extensions: ['.json', '.js',],
  },
  module: {
    rules: [
      {
        test: /\.svg$/i,
        exclude: /node_modules/,
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
        exclude: /node_modules/,
        use: ['css-loader', 'resolve-url-loader', 'sass-loader'],
      },
      {
        test: /\.css$/i,
        exclude: /node_modules/,
        use: [
          {
            loader: 'css-loader',
            options: {
              importLoaders: 1,
            },
          },
          {
            loader: 'postcss-loader',
          },
        ],
      },
      {
        test: /\.(ttf|woff|woff2)$/i,
        exclude: /node_modules/,
        loader: 'file-loader',
        options: {
          name: '[name].[ext]',
          outputPath: 'fonts',
        },
      },
      {
        test: /\.(jpg|png|gif)$/i,
        exclude: /node_modules/,
        loader: 'file-loader',
        options: {
          name: '[name].[ext]',
          outputPath: 'images',
        },
      },
    ],
  },
}