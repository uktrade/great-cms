const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const RemovePlugin = require('remove-files-webpack-plugin')

module.exports = {
  devtool: 'source-map',
  entry: {
    magna: './react-components/src/bundle.js',
    magna_styles: './core/sass/magna.scss',
    learn_styles: './core/sass/main.scss',
    common: './core/js/common.js',
    largevideoupload: './core/js/largevideoupload.js',
    custom_wagtaildraftailanchors: "./core/js/custom_wagtaildraftailanchors/wagtail_draftail_anchor.js",
    modifyAnchorLinkLabel: "./core/js/modifyAnchorLinkLabel.js",
    loggedout_styles: './domestic/sass/main.scss',
    components: './react-components/src/bundle-components.js',
    components_styles:
      './core/components/sass/components/elements-components.scss',
    profile_styles: './sso_profile/common/sass/profile.scss',
    international_styles: './international/sass/main.scss',
    expand_your_business_styles: './international_online_offer/sass/main.scss',
    investment_styles: './international_investment/sass/main.scss',
    microsite_styles: './styles/microsite/main.scss',
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
              url: {
                filter: (url) => url.match('/node_modules/'),
              },
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
              sourceMap: true,
              sassOptions: {
                outputStyle: 'compressed',
                includePaths: [
                  './node_modules/great-styles/src/scss/',
                  './styles/',
                  './domestic/sass/',
                  './core/components/sass/components/',
                  './sso_profile/common/sass/partials/',
                ],
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
        test: [
          {
            folder: './react-components/dist',
            method: (absoluteItemPath) => {
              return new RegExp(/_styles\.js(\.map)?$/).test(absoluteItemPath)
            },
          },
        ],
      },
    }),
  ],
  stats: {
    children: true,
  },
}
