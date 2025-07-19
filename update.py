#!/usr/bin/env python3
from logging import (
    FileHandler, StreamHandler, INFO,
    basicConfig, error as log_error, info as log_info
)
from os import path as ospath, environ, remove
from subprocess import run as srun, call as scall
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient
from importlib.metadata import distributions

# Clear previous logs
if ospath.exists("log.txt"):
    with open("log.txt", "w") as f:
        f.truncate(0)
if ospath.exists("rlog.txt"):
    remove("rlog.txt")

# Setup logging
basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

# Load config.env
env_path = Path("config.env")
load_dotenv(dotenv_path=env_path, override=True)

# Exit early if README placeholder present
if environ.get("_____REMOVE_THIS_LINE_____"):
    log_error("You forgot to edit your config file! Exiting.")
    exit(1)

# Required vars
BOT_TOKEN = environ.get("BOT_TOKEN", "")
DATABASE_URL = environ.get("DATABASE_URL", "")
if not BOT_TOKEN or not DATABASE_URL:
    log_error("BOT_TOKEN or DATABASE_URL is missing in your config.env! Exiting.")
    exit(1)

bot_id = BOT_TOKEN.split(":", 1)[0]

try:
    # Connect to MongoDB
    conn = MongoClient(DATABASE_URL)
    db = conn.wzmlx
    env_vars = dict(dotenv_values(env_path))
    old_config = db.settings.deployConfig.find_one({"_id": bot_id})
    config_dict = db.settings.config.find_one({"_id": bot_id})

    if old_config:
        del old_config["_id"]

    if (
        old_config is None or old_config == env_vars
    ) and config_dict is not None:
        # Update local env if remote config present
        environ["UPSTREAM_REPO"] = config_dict["UPSTREAM_REPO"]
        environ["UPSTREAM_BRANCH"] = config_dict.get("UPSTREAM_BRANCH", "master")
        environ["UPGRADE_PACKAGES"] = config_dict.get("UPDATE_PACKAGES", "False")
    conn.close()

except Exception as e:
    log_error(f"MongoDB error: {e}")
    exit(1)

# Upgrade pip packages if required
if environ.get("UPGRADE_PACKAGES", "").lower() == "true":
    pkgs = [dist.metadata["Name"] for dist in distributions()]
    scall("uv pip install --system " + " ".join(pkgs), shell=True)

# Git repo updater
UPSTREAM_REPO = environ.get("UPSTREAM_REPO", "")
UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH", "master")

if UPSTREAM_REPO:
    if ospath.exists(".git"):
        srun(["rm", "-rf", ".git"])

    cmd = (
        f"git init -q && "
        f"git config --global user.email doc.adhikari@gmail.com && "
        f"git config --global user.name weebzone && "
        f"git add . && "
        f"git commit -sm update -q && "
        f"git remote add origin {UPSTREAM_REPO} && "
        f"git fetch origin -q && "
        f"git reset --hard origin/{UPSTREAM_BRANCH} -q"
    )

    result = srun(cmd, shell=True)

    clean_repo_url = f"https://github.com/{UPSTREAM_REPO.split('/')[-2]}/{UPSTREAM_REPO.split('/')[-1]}"
    if result.returncode == 0:
        log_info("✅ Successfully updated with latest commits!")
    else:
        log_error("❌ Update failed! Try again or check your repo.")
    log_info(f"REPO: {clean_repo_url} | BRANCH: {UPSTREAM_BRANCH}")