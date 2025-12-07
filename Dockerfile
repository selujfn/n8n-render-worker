# Utiliser une image Python de base avec Debian (qui supporte les outils système)
FROM python:3.10-slim

# Installer les dépendances système nécessaires pour moviepy (FFMPEG)
RUN apt-get update && apt-get install -y ffmpeg

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Définir la variable PORT pour Render.com
ENV PORT 10000

# Exposer le port (utile pour l'info, Render utilise le port ENV)
EXPOSE 10000

# Commande de démarrage (remplace le Procfile dans ce cas)
CMD exec gunicorn --bind 0.0.0.0:$PORT render_app:app
