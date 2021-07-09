DJANGO_APPS=(
  "directory-api"
  "directory-forms-api"
  "directory-sso"
  "directory-sso-proxy"
  )

cd ..

for app in "${DJANGO_APPS[@]}"
do
    echo "Initalising: $app"

    if [ ! -d $app ]; then
        git clone https://github.com/uktrade/$app
    fi

    cd $app
    make secrets
    echo ""
    cd ..
done

echo "Initialising great-cms"
cd great-cms
make secrets
echo ""

echo "The following environment variables are required:

great-cms:
    AWS_STORAGE_BUCKET_NAME
    AWS_SECRET_ACCESS_KEY
    AWS_ACCESS_KEY_ID
    AWS_S3_REGION_NAME
directory-forms-api:
    GOV_NOTIFY_API_KEY
    GOV_NOTIFY_LETTER_API_KEY

These variables need to be added to the respective conf(ig)/env/secrets-do-not-commit files.
"

read -e -p "Have all the variables above been added? [Y/n] " YN

if [[ $YN != "y" && $YN != "Y" && $YN != "" ]]; then
    echo "Please setup the variables above and run this script again."
    exit 1
fi

echo "Starting docker build...\n"
docker-compose -f development.yml build --no-cache

echo "Starting docker containers...\n"
docker-compose -f development.yml up
