module.exports = {
  moduleFileExtensions: ["js", "jsx"],
  moduleNameMapper: {
    "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$":
      "<rootDir>/react-components/tests/imageMock.js",
    "^.+\\.(css|scss)$": "<rootDir>/react-components/tests/css-stub.js",
    "^@src(.*)$": "<rootDir>/react-components/src/$1",
    "^@assets(.*)$": "<rootDir>/react-components/assets/$1",
  },
  moduleDirectories: ["node_modules"],
  transform: {
    "^.+\\.jsx?$": "babel-jest",
  },
  setupFiles: [
    "<rootDir>/react-components/setupEnzyme.js",
    "<rootDir>/react-components/setupJest.js",
  ],
};
