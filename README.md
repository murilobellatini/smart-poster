# SmartPoster

Application for generating social media posts automatically. In a smart way 🤓.

## How to setup

### Requirements

#### Packages

* Python >= 3.8
* `pipenv`

#### Environment variables

* `UNSPLASH_ACCESS_KEY`: Access key for Unsplash API
* `UNSPLASH_SECRET_KEY`: Secret key for Unsplash API
* `GCP_KEY`: Google Cloud key with Image Custom Search enabled
* `GCX`: Google context

Note:

> Alternatively creat `.env` file at root of repo for setting env vars.

#### Credentials

* `/credentials/gcloud.json`: Place here the json file for Google Cloud Service Account.


### Step-by-step

1. Setup env vars and credentials
2. Install packages

```bash
cd <REPO_ROOT_PATH>
pipenv shell
pip install -r requirements
```

3. Run Jupyter Notebooks at will