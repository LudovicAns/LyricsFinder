echo "Installation de l'envronnement virtuel ..."
python -m venv virtualenv
cd virtualenv/Scripts/ || exit
. ./activate
pip install bs4
pip install requests
python -m pip install --upgrade pip
