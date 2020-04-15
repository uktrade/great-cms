const path = require("path")
const MiniCssExtractPlugin = require("mini-css-extract-plugin")
const CopyWebpackPlugin = require("copy-webpack-plugin")
const RemovePlugin = require("remove-files-webpack-plugin")
const nodeSass = require("node-sass")

module.exports = {
  devtool: "source-map",
  entry: {
    ditMVP: "./react-components/src/bundle.js",
  },
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].js",
    publicPath: "",
    library: "[name]",
    libraryExport: "default",
    libraryTarget: "var",
  },
  resolve: {
    extensions: [".js", ".jsx"],
    alias: {
      "@src": path.resolve(__dirname, "src"),
      "@assets": path.resolve(__dirname, "assets"),
    },
  },
  module: {
    rules: [
      // {
      //   enforce: "pre",
      //   test: /\.jsx?$/,
      //   exclude: /node_modules/,
      //   loader: "eslint-loader",
      // },
      {
        test: /\.jsx?$/,
        loader: "babel-loader",
        options: {
          presets: [
            "@babel/preset-env",
            "@babel/react",
            {
              plugins: ["@babel/plugin-proposal-class-properties"],
            },
          ],
        },
        exclude: /node_modules/,
      },
      {
        test: /\.s?css$/i,
        use: [
          // extract to seperate file
          MiniCssExtractPlugin.loader,
          // Translates CSS into CommonJS
          {
            loader: "css-loader",
            options: {
              sourceMap: true,
            },
          },
          // Compiles Sass to CSS
          {
            loader: "sass-loader",
            options: {
              implementation: nodeSass,
              sourceMap: true,
              sassOptions: {
                outputStyle: "compressed",
                includePaths: ["./node_modules/great-styles/src/"],
              },
            },
          },
        ],
      },
      {
        test: /\.(jpg|png|gif|jpeg|woff|woff2|eot|ttf|svg)$/,
        loader: "url-loader?limit=10000&name=img/[name].[ext]",
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin(),
    new CopyWebpackPlugin([
      { from: "./node_modules/great-styles/src/images", to: "images" },
      // copies the images to core/static only if not present. This avoids
      // the svg files showing up in diff every time a new build occurs
      { from: "react-components/dist/img/", to: "../../core/static/img/" },
    ]),
    new RemovePlugin({ after: { include: ["./react-components/dist/img/"] } }),
  ],
}
