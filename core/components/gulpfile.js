'use strict';

const path = require('path');
const gulp = require('gulp');
const gutil = require('gulp-util');
const cssnano = require('gulp-cssnano');
const sourcemaps = require('gulp-sourcemaps');
const del = require('del');
const rename = require('gulp-rename');
const runsequence = require('run-sequence');
const sass = require('gulp-sass');
const sassLint = require('gulp-sass-lint');
const autoprefixer = require('gulp-autoprefixer');

const PROJECT_DIR = path.resolve(__dirname);
const FLAGS_SRC = [
  `${PROJECT_DIR}/node_modules/flag-icon-css/**/*.svg`,
  `${PROJECT_DIR}/node_modules/flag-icon-css/**/*.min.css`,
];
const FLAGS_DEST = `${PROJECT_DIR}/static/vendor/flag-icons`;

// Sass lint -----------------------------

gulp.task('lint:sass', function () {
  return gulp.src('/**/*.scss')
    .pipe(sassLint({
      options: {
        formatter: 'stylish',
        'merge-default-rules': true
      },
      configFile: 'sass-lint-config.yml'
    }))
    .pipe(sassLint.format())
    .pipe(sassLint.failOnError());
});


// Run tests -----------------------------

gulp.task('test', () => {
  runsequence(['lint:sass'], cb => {
    if (cb) {
      gutil.log(gutil.colors.red('!!!!!!!! Tests failed !!!!!!!!'));
    } else {
      gutil.log(gutil.colors.green('**** Tests finished with no errors ****'));
    }
  });
});

// Clean task ----------------------------
// Deletes the /static/stylesheets/ directory
// ---------------------------------------

gulp.task('clean', () => {
  return del('/static/stylesheets/');
});

// GovUK styles build task ---------------
// Compiles CSS from Sass
// Output both a minified and non-minified version into
// /static/stylesheets/
// ---------------------------------------

gulp.task('styles:govuk', function() {
  return gulp.src('node_modules/govuk-elements/assets/sass/**/*.scss')
    .pipe(sourcemaps.init())
    .pipe(sass({
      includePaths: [
        'node_modules/govuk_frontend_toolkit/stylesheets',
      ],
      importer: require('./sass-importer.js')
    }).on('error', sass.logError))
    .pipe(autoprefixer({
      browsers: ['last 2 versions'],
      cascade: false
    }))
    .pipe(gulp.dest('static/stylesheets'))
    .pipe(rename({ suffix: '.min' }))
    .pipe(cssnano())
    .pipe(sourcemaps.write('./maps'))
    .pipe(gulp.dest('static/stylesheets'));
});

// Export-elements-specific component styling

gulp.task('styles:components', () => {
  return gulp.src('sass/components/elements-components.scss')
    .pipe(sourcemaps.init())
    .pipe(sass().on('error', sass.logError))
    .pipe(autoprefixer({
      browsers: ['last 2 versions'],
      cascade: false
    }))
    .pipe(gulp.dest('static/stylesheets'))
    .pipe(rename({ suffix: '.min' }))
    .pipe(cssnano())
    .pipe(sourcemaps.write('./maps'))
    .pipe(gulp.dest('static/stylesheets'));
});

// Flag icons

gulp.task('flags', function() {
  return gulp.src(FLAGS_SRC)
  .pipe(gulp.dest(FLAGS_DEST));
});

// Compile all styles

gulp.task('styles', [
  'styles:govuk',
  'styles:components',
]);

// Images build task ---------------------
// Copies images to /static/images
// ---------------------------------------

gulp.task('images', () => {
  return gulp.src([
    'node_modules/govuk-elements/assets/images/**/*',
    'node_modules/govuk_frontend_toolkit/images/**/*'
  ])
    .pipe(gulp.dest('static/images'));
});

// Build task ----------------------------
// Runs tasks that copy assets to the
// /static/ directory.
// ---------------------------------------

gulp.task('build', cb => {
  runsequence('clean', ['styles', 'images', 'flags'], cb);
});

// Watch task ----------------------------
// When a file is changed, re-run the build task.
// ---------------------------------------

gulp.task('watch', () => {
  return gulp.watch([
    './**/*.scss'
  ], ['styles']);
});

// Default task --------------------------
// Lists out available tasks.
// ---------------------------------------

gulp.task('default', () => {
  const cyan = gutil.colors.cyan;
  const green = gutil.colors.green;

  gutil.log(green('----------'));

  gutil.log(('The following main ') + cyan('tasks') + (' are available:'));

  gutil.log(cyan('build') + ': compiles assets.');
  gutil.log(cyan('watch') + ': compiles assets and watches for changes.');
  gutil.log(cyan('test') + ': runs tests/lint.');

  gutil.log(green('----------'));
});
