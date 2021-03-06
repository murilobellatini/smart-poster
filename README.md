# SmartPoster

Application for generating social media posts automatically. In a smart way 🤓.

Check out our experimental Instagram profile with auto-generated posts (image and caption).

> Instagram Profile: [📸 the.wisdom.drops](https://www.instagram.com/the.wisdom.drops/)

## Examples

![image](https://user-images.githubusercontent.com/43999445/132679748-7ba155b2-b1ad-4136-a403-9d49ec15d03a.png)

## Usage

```bash
usage: main.py [-h] -t THEMES -c POST_COUNT_PER_THEME

optional arguments:
    -h, --help      show this help message and exit
    -t THEMES, --themes THEMES
                    string of themes to generate the posts about; Enter multiple ones separated by comma `,`
    -c POST_COUNT_PER_THEME, --post_count_per_theme POST_COUNT_PER_THEME
                    amount of posts per theme
```

**Note**
> Posts generated according configuration set in `config.yaml` file.

## How to setup

### Requirements

#### Packages

* Python >= 3.8
* `pipenv`

#### Environment variables

##### Required
* `UNSPLASH_ACCESS_KEY`: Access key for Unsplash API
* `UNSPLASH_SECRET_KEY`: Secret key for Unsplash API
* `GCP_KEY`: Google Cloud key with Image Custom Search enabled
* `GCX`: Google context

##### Not implemented yet (Facebook API)
* `FB_ACCESS_TOKEN`: Token for interacting with Facebook Graph API (with basic privileges)
* `FB_ACCESS_TOKEN_SANDBOX`: Token with advanced privileges for using Marketing API features
* `AD_ACCOUNT_ID`: Account ID for interacting with Business Data

**Note**

> Alternatively create `.env` file at root of repo for setting env vars.

#### Credentials

* `./credentials/gcloud.json`: Place here the json file for Google Cloud Service Account.


### Step-by-step

1. Setup env vars and credentials
2. Install packages

```bash
cd <REPO_ROOT_PATH>
pipenv shell
pip install -r requirements.txt
```

3. Run script from cli (check `Usage` above)
