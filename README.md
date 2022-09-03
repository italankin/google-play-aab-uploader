# Google Play AAB Uploader

A script for uploading Android App Bundles to Google Play Store.

## Usage

```sh
$ python3 upload.py \
    --package-name 'com.example.myapp' \
    --key-path '/path/to/service/account/key/file' \
    --aab-path '/path/to/aab/file'
```

## Docker image

Docker image is available at [ghcr.io](https://ghcr.io/italankin/google-play-aab-uploader).

### Run in docker

```sh
$ docker run --rm -it \
    -v "$(pwd)/com.example.myapp.aab":'/data/bundle.aab' \
    -v "$(pwd)/service-account-key.json":'/data/key.json' \
    ghcr.io/italankin/google-play-aab-uploader \
    --package-name 'com.example.myapp' \
    --key-path '/data/key.json' \
    --aab-path '/data/bundle.aab'
```
