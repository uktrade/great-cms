const sass = require('gulp-sass')(require('sass'))
const path = require('path')
const gulp = require('gulp')
const sourcemaps = require('gulp-sourcemaps')
const del = require('del')
const rename = require('gulp-rename')
const autoprefixer = require('gulp-autoprefixer')
const cleanCSS = require('gulp-clean-css');

const PROJECT_DIR = path.resolve(__dirname)
const FLAGS_SRC = [
  `${PROJECT_DIR}/node_modules/flag-icon-css/**/*.svg`,
  `${PROJECT_DIR}/node_modules/flag-icon-css/**/*.min.css`,
]
const FLAGS_DEST = `${PROJECT_DIR}/static/vendor/flag-icons`


// // Clean task ----------------------------
// // Deletes the /static/stylesheets/ directory
// // ---------------------------------------

gulp.task(
  'clean',
  gulp.series(() => {
    return del('/static/stylesheets/')
  })
)

// // Export-elements-specific component styling

gulp.task(
  'styles:components',
  gulp.series(() => {
    return gulp
      .src('sass/components/elements-components.scss')
      .pipe(sourcemaps.init())
      .pipe(sass().on('error', sass.logError))
      .pipe(
        autoprefixer({
          browsers: ['last 2 versions'],
          cascade: false,
        })
      )
      .pipe(gulp.dest('static/stylesheets'))
      .pipe(rename({ suffix: '.min' }))
      .pipe(cleanCSS({compatibility: 'ie8'}))
      .pipe(sourcemaps.write('./maps'))
      .pipe(gulp.dest('static/stylesheets'))
  })
)

// // Flag icons

gulp.task(
  'flags',
  gulp.series(function () {
    return gulp.src(FLAGS_SRC).pipe(gulp.dest(FLAGS_DEST))
  })
)

// // Compile all styles

gulp.task('sass:compile', gulp.series('styles:components'))

// // Images build task ---------------------
// // Copies images to /static/images
// // ---------------------------------------

gulp.task(
  'images',
  gulp.series(() => {
    return gulp
      .src([
        'node_modules/govuk-elements/assets/images/**/*',
        'node_modules/govuk_frontend_toolkit/images/**/*',
      ])
      .pipe(gulp.dest('static/images'))
  })
)

// // Build task ----------------------------
// // Runs tasks that copy assets to the
// // /static/ directory.
// // ---------------------------------------

gulp.task('build', gulp.series('clean', 'sass:compile', 'images', 'flags'))

// // Watch task ----------------------------
// // When a file is changed, re-run the build task.
// // ---------------------------------------

gulp.task('sass:watch', () => {
  gulp.watch(['./**/*.scss'], gulp.series('sass:compile'))
})
