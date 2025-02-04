echo "Adding Python repository..."
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update -y
echo "Python repo added."

echo "Installing Python 3.12..."
sudo apt install python3.12 python3.12-venv -y
echo "Python version: $(python3 --version)"

echo "Installing NVM and Node.js..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 22
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

echo "Installing Java..."
sudo apt install fontconfig openjdk-17-jre -y
echo "Java version: $(java --version)"

echo "Adding Jenkins repository and installing Jenkins..."
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update -y
sudo apt-get install jenkins -y
sudo systemctl enable jenkins
sudo systemctl start jenkins
echo "Jenkins installed."
echo "Jenkins password: $(sudo cat /var/lib/jenkins/secrets/initialAdminPassword)"

echo "Installing and starting Nginx..."
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
echo "Nginx started."

echo "Building frontend..."
cd frontend
npm i
npm run build
sudo cp -r dist/* /var/www/html/
sudo systemctl restart nginx
echo "Frontend built."

echo "Setting up backend..."
cd ..
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Backend setup complete."

echo "Configuring FastAPI service..."
sudo touch /etc/systemd/system/fastapi.service
sudo cat fastapi.service > /etc/systemd/system/fastapi.service
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
echo "FastAPI service configured."

echo "Initialization complete."