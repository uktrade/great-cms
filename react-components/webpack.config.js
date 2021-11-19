const path = require('path')
const glob = require("glob");
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const RemovePlugin = require('remove-files-webpack-plugin')

module.exports = {
  devtool: 'source-map',
  entry: {
    magna: './react-components/src/bundle.js',
    magna_styles: './core/sass/main.scss',
    loggedout: './react-components/src/bundle-loggedout.js',
    loggedout_styles: './domestic/sass/main.scss',
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
    publicPath: '',
    library: '[name]',
    libraryExport: 'default',
    libraryTarget: 'var',
  },
  resolve: {
    fallback: { buffer: require.resolve('safe-buffer') },
    extensions: ['.js', '.jsx'],
    alias: {
      '@src': path.resolve(__dirname, 'src'),
      '@assets': path.resolve(__dirname, 'assets'),
      '@components': path.resolve(
        __dirname,
        '../node_modules/great-styles/dist/components/'
      ),
    },
    fallback: {
      buffer: false,
    },
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        options: {
          presets: [
            '@babel/preset-env',
            '@babel/react',
            {
              plugins: ['@babel/plugin-proposal-class-properties'],
            },
          ],
        },
        exclude: /node_modules/,
      },
      {
        test: /\.scss$/i,
        exclude: /node_modules/,
        use: [
          // extract to separate file
          MiniCssExtractPlugin.loader,
          // Translates CSS into CommonJS
          {
            loader: 'css-loader',
            options: {
              sourceMap: true,
            },
          },
          {
            loader: 'resolve-url-loader',
            options: {
              sourceMap: true,
            },
          },
          // Compiles Sass to CSS
          {
            loader: 'sass-loader',
            options: {
              implementation: require('sass'),
              sourceMap: true,
              sassOptions: {
                outputStyle: 'compressed',
                includePaths: ['./node_modules/great-styles/src/scss/', './domestic/sass/'],
              },
            },
          },
        ],
      },
      {
        test: /\.css$/,
        exclude: /node_modules/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: true,
            },
          },
        ],
      },
      {
        test: /\.(jpg|png|gif|jpeg|svg)$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: 'img/[name].[ext]',
        },
      },
      {
        test: /\.(woff|woff2|eot|ttf)$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: 'fonts/[name][ext]',
        },
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css',
    }),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: './node_modules/great-styles/static/images',
          to: 'images',
          noErrorOnMissing: true,
        },
        {
          from: './node_modules/great-styles/static/fonts',
          to: '../../core/static/fonts/',
          noErrorOnMissing: true,
        },
        // copies the images to core/static only if not present. This avoids
        // the svg files showing up in diff every time a new build occurs
        {
          from: 'react-components/dist/img/',
          to: '../../core/static/img/',
          noErrorOnMissing: true,
        },
        {
          from: 'react-components/dist/fonts/',
          to: '../../core/static/fonts/',
          noErrorOnMissing: true,
        },
        // copy assets needed by CSS files as they are not automatically moved to dist foler by React
        {
          from: 'react-components/assets/stylesheet-assets/',
          to: '../../core/static/img/',
          noErrorOnMissing: true,
        },
      ],
    }),
    new RemovePlugin({
      after: {
        include: [
          './react-components/dist/magna_styles.js',
          './react-components/dist/magna_styles.js.map',
          './react-components/dist/magna.css',
          './react-components/dist/magna.css.map',
          './react-components/dist/loggedout_styles.js',
          './react-components/dist/loggedout_styles.js.map',
          './react-components/dist/magna.js.LICENSE.txt',
          './react-components/dist/loggedout.js.LICENSE.txt',
        ],
      },
    }),
  ],
  stats: {
    children: true
  },
}
