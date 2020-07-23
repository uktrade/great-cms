const path = require('path')
const nodeSass = require('node-sass')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  resolve: {
    modules: ['../', '../node_modules'],
    extensions: ['.json', '.js',],
    alias: {
      '@src': path.resolve(__dirname, '../react-components/src'),
      '@assets': path.resolve(__dirname, '../react-components/assets')
    }
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
        test: /\.scss/,
        use: [
          { loader: 'style-loader' },
          { loader: 'css-loader' },
          {
            loader: 'sass-loader',
            options: {
              implementation: nodeSass,
              sassOptions: {
                outputStyle: 'compressed',
                includePaths: ['node_modules/great-styles/src', 'core/sass']
              }
            }
          },
        ],
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
