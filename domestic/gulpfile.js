const path = require('path')
const gulp = require('gulp')
const sass = require('gulp-sass')(require('node-sass'))
const sourcemaps = require('gulp-sourcemaps')
const del = require('del')

const PROJECT_DIR = path.resolve(__dirname)
const SASS_FILES = `${PROJECT_DIR}/sass/**/*.scss`
const CSS_DIR = `${PROJECT_DIR}/static/styles`
const CSS_FILES = `${PROJECT_DIR}/static/styles/**/*.css`
const CSS_MAPS = `${PROJECT_DIR}/static/styles/**/*.css.map`

gulp.task(
  'clean',
  gulp.series(() => {
    return del([CSS_FILES, CSS_MAPS])
  }),
)

gulp.task(
  'sass:compile',
  gulp.series(() => {
    return gulp
      .src(SASS_FILES)
      .pipe(sourcemaps.init())
      .pipe(
        sass({
          includePaths: ['./conf/'],
          outputStyle: 'compressed',
        }).on('error', sass.logError),
      )
      .pipe(sourcemaps.write('./maps'))
      .pipe(gulp.dest(CSS_DIR))
  })
)

gulp.task('sass:watch', () => {
  gulp.watch([SASS_FILES], gulp.series('sass:compile'))
})

gulp.task('build', gulp.series('clean', 'sass:compile'))
