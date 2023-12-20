sudo docker stop $(sudo docker ps -a -q)
sudo docker rm $(sudo docker ps -a -q)
sudo docker-compose up --build

# SAFER ALTERNATIVE: sudo usermod -aG docker $USER