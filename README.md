# Google Play AAB Uploader

A script for uploading Android App Bundles to Google Play Store.

## Usage

```sh
$ pip install -r requirements.txt
$ python3 upload.py \
    --package-name 'com.example.myapp' \
    # to pass JSON instead of file, use --key-json
    --key-path '/path/to/service/account/key/file' \
    --aab-path '/path/to/aab/file'
```

### GitHub Actions

Example of usage in GitHub Actions workflow:

```yaml
steps:
  # ...

  - name: Upload AAB
    uses: italankin/google-play-aab-uploader@1.3
    with:
      package-name: 'com.example.app'
      aab-path: 'app/build/outputs/bundle/release/app-release.aab'
      key-json: '${{ secrets.SERVICE_KEY_JSON }}'
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

You can also use it with CI tools like Drone:

```yaml
kind: pipeline
type: docker
name: upload-bundle

steps:
  ...
  - name: upload
    image: ghcr.io/italankin/google-play-aab-uploader
    environment:
      GOOGLE_PLAY_KEY_BASE64:
        from_secret: google_play_key_base64
    commands:
      - echo "$GOOGLE_PLAY_KEY_BASE64" | base64 -d > key.json
      - >
        python /google-play-uploader/upload.py \
          --package-name com.example.myapp \
          --key-path key.json \
          --aab-path app/build/outputs/bundle/release/app-release.aab
```
