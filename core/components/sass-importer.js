const path = require('path');
const fs = require('fs');
const resolve = require('@csstools/sass-import-resolve');


const overridePath = path.join(__dirname, 'directory_components/export_elements/overrides/');
const listDirectories = source =>
  fs.readdirSync(source)
    .map(name => path.join(source, name))
    .filter(name => fs.lstatSync(source).isDirectory());

module.exports = function(url, prev, done) {
  if (url.indexOf('!') === 0) {
    return {file: url.substr(1)};
  }

  const includePaths = listDirectories(overridePath).concat(
    [path.dirname(prev)],
    this.options.includePaths.split(':')
  );


  const promises = includePaths.map(importPath =>
    new Promise(success => resolve(url, {cwd: importPath})
        .then(success)
        .catch(() => {})
      )
  );

  Promise.race(promises).then(done).catch(done);
};
