const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');


module.exports = {
    devtool: 'source-map',
    entry: {
        'ditMVP': './react-components/src/bundle.js',
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].js',
        publicPath: '',
        library: '[name]',
        libraryExport: 'default',
        libraryTarget: 'var'
    },
    resolve: {
        extensions: ['.js', '.jsx'],
        alias: {
          '@src': path.resolve(__dirname, 'src'),
          '@assets': path.resolve(__dirname, 'assets'),
        }
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                loader: 'babel-loader',
                options: {
                  presets: [
                    '@babel/preset-env',
                    '@babel/react',{
                    'plugins': ['@babel/plugin-proposal-class-properties']}]
                },
                exclude: /node_modules/
            },
              {
                test: /\.scss$/i,
                use: [
                  // extract to seperate file
                  MiniCssExtractPlugin.loader,
                  // Translates CSS into CommonJS
                  {
                    loader: 'css-loader',
                    options: {
                      sourceMap: true,
                    },
                  },
                  // Compiles Sass to CSS
                  {
                    loader: 'sass-loader',
                    options: {
                      implementation: require('node-sass'),
                      sourceMap: true,
                      sassOptions: {
                        outputStyle: 'compressed',
                        includePaths: ['./node_modules/great-styles/src/'],
                      },
                    },
                  },
                ],
              },
            {
              test: /\.(jpg|png|gif|jpeg|woff|woff2|eot|ttf|svg)$/,
              loader: 'url-loader?limit=10000&name=img/[name].[ext]'
            }
        ]
    },
    plugins: [
      new MiniCssExtractPlugin(),
      new CopyWebpackPlugin([{from: './node_modules/great-styles/src/images', to: 'images'}]),
    ],
};
