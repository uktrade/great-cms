const path = require('path');

module.exports = {
    entry: {
        'reactComponents': './react-components/src/bundle.js',
    },
    output: {
        path: path.resolve(__dirname, '../directory_components/static/directory_components/js/'),
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
            }
        ]
    }
};