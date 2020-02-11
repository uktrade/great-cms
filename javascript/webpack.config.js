const path = require('path');


const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: {
        'ditMVP': './javascript/src/bundle.js',
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
        extensions: ['.js', '.jsx']
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                loader: 'babel-loader',
                exclude: /node_modules/
            },
              {
                test: /\.scss$/i,
                use: [
                  // Creates `style` nodes from JS strings
                  'style-loader',
                  // extract to seperate file
                  MiniCssExtractPlugin.loader,
                  // Translates CSS into CommonJS
                  'css-loader',
                  // Compiles Sass to CSS
                  'sass-loader',
                ],
              },
            {
                test: /\.(jpg|png|gif|jpeg|woff|woff2|eot|ttf|svg)$/,
                loader: 'url-loader?limit=10000&name=img/[name].[ext]'
            }
        ]
    },
    plugins: [new MiniCssExtractPlugin()],
};