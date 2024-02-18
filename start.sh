if [ -z "$UPSTREAM_REPO" ]; then
  echo "Cloning main Repository"
  git clone -b notshort https://github.com/Mayavar258/Flts.git /Flts
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone -b notshort --single-branch "$UPSTREAM_REPO" /Flts
fi

cd /Flts
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
