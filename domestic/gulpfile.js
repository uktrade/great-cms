'use strict'
const path = require('path')
const gulp = require('gulp')
const sass = require('gulp-sass')
const sourcemaps = require('gulp-sourcemaps')
const del = require('del')

const PROJECT_DIR = path.resolve(__dirname)
const SASS_FILES = `${PROJECT_DIR}/sass/**/*.scss`
const CSS_DIR = `${PROJECT_DIR}/static/styles`
const CSS_FILES = `${PROJECT_DIR}/static/styles/**/*.css`
const CSS_MAPS = `${PROJECT_DIR}/static/styles/**/*.css.map`

gulp.task(
  'clean',
  gulp.series(function () {
    return del([CSS_FILES, CSS_MAPS])
  })
)

gulp.task(
  'sass:compile',
  gulp.series(function () {
    return gulp
      .src(SASS_FILES)
      .pipe(sourcemaps.init())
      .pipe(
        sass({
          includePaths: ['./conf/'],
          outputStyle: 'compressed',
        }).on('error', sass.logError)
      )
      .pipe(sourcemaps.write('./maps'))
      .pipe(gulp.dest(CSS_DIR))
  })
)

gulp.task('sass:watch', () => {
  gulp.watch([SASS_FILES], gulp.series('sass:compile'))
})

gulp.task('build', gulp.series('clean', 'sass:compile'))

gulp.task(
  'default',
  gulp.series((done) => {
    const cyan = gutil.colors.cyan
    const green = gutil.colors.green

    gutil.log(green('----------'))

    gutil.log('The following main ' + cyan('tasks') + ' are available:')

    gutil.log(cyan('build') + ': compiles assets.')
    gutil.log(cyan('sass:watch') + ': compiles assets and watches for changes.')

    gutil.log(green('----------'))
    done()
  })
)
